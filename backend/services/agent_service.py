import json
import logging
from tools import execute_tool
from typing import AsyncGenerator
from services.ai_service import get_ai_service
from services.session_manager import session_manager
from services.system_prompt import SYSTEM_PROMPT
from services.settings_service import settings_service
from utils.stream_utils import parse_stream_token, StreamResult

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def _setup_chat_history(self, prompt: str, session_id: str) -> list:
        """Setup chat history with session context"""
        # Build system prompt with user rules
        system_prompt = self._build_system_prompt()

        chat_history = [{"role": "system", "content": system_prompt}]

        # Add last three loops
        context_messages = session_manager.get_context_for_ai(session_id)
        chat_history.extend(context_messages)

        # Add user prompt
        chat_history.append({
            "role": "user",
            "content": prompt
        })

        return chat_history

    def _build_system_prompt(self) -> str:
        """Build system prompt with base prompt plus user-defined rules"""
        system_prompt = self.system_prompt

        # Get user rules
        user_rules = settings_service.get_rules()

        if user_rules:
            # Add user rules section
            rules_text = "\n\nUSER-DEFINED RULES:\n"
            for i, rule in enumerate(user_rules, 1):
                if isinstance(rule, dict) and 'text' in rule:
                    rules_text += f"{i}. {rule['text']}\n"
                else:
                    rules_text += f"{i}. {rule}\n"

            system_prompt += rules_text

        return system_prompt

    async def _process_ai_stream(self, chat_history: list) -> tuple:
        """Process AI response stream and return parsed results"""
        accumulated = ""
        finish_buffer = ""
        streamed_fields = set()
        thought_buffer = None

        # Initialize result to prevent UnboundLocalError
        result = None

        ai_service_instance = get_ai_service()
        async for token in ai_service_instance.chat_stream_with_context(chat_history):
            result = parse_stream_token(token, accumulated, finish_buffer, streamed_fields, thought_buffer)

            # Update state
            accumulated = result.accumulated
            finish_buffer = result.finish_buffer
            streamed_fields = result.streamed_fields
            thought_buffer = result.thought_buffer

            # Stream outputs
            for output in result.outputs:
                yield output

            # Check for completion
            if result.is_complete:
                break

        # Return final results with fallback if no result was ever created
        if result is None:
            # Handle empty stream case, no tokens were received
            logger.warning("AI stream returned no tokens, using empty response")
            result = StreamResult(
                outputs=[],
                accumulated="",
                finish_buffer="",
                streamed_fields=set(),
                is_complete=True,
                final_answer="I apologize, but I couldn't generate a response. Please try again.",
                thought_buffer={"has_thought": False, "thought_content": "", "thought_streamed": False}
            )
            accumulated = ""
            streamed_fields = set()

        action_streamed = "action" in streamed_fields
        yield accumulated, result.is_complete, action_streamed, result.final_answer

    def _handle_tool_execution(self, accumulated_response: str, chat_history: list, tool_results_used: list, job_name: str = None):
        """Execute tool and update chat history"""
        try:
            response_data = json.loads(accumulated_response)
            tool_name = response_data["action"]["name"]
            tool_input = response_data["action"]["input"]

            # Parse tool_input and add job_name if needed
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    tool_input = {"query": tool_input}

            if isinstance(tool_input, dict) and job_name and "job_name" not in tool_input:
                tool_input["job_name"] = job_name

            # Execute tool
            tool_result = execute_tool(tool_name, tool_input)
            tool_results_used.append(tool_result)

            # Check if tool execution failed due to non-existent tool
            if not tool_result.get("success") and "not found" in tool_result.get("error", ""):
                error_type = tool_result.get("error_type")
                if error_type in ["report_not_found", "artifact_not_found"]:
                    # Use educational feedback directly
                    enhanced_error_message = tool_result.get("error")
                else:
                    # Handle generic "not found" errors
                    from tools import TOOLS
                    available_tools = list(TOOLS.keys())
                    enhanced_error_message = f"Tool '{tool_name}' does not exist. Available tools are: {', '.join(available_tools)}. Please use one of the available tools or provide your final answer in the Final format."

                # Add the original response and enhanced error message to chat
                chat_history.append({
                    "role": "assistant",
                    "content": accumulated_response
                })
                chat_history.append({
                    "role": "user",
                    "content": f"Error: {enhanced_error_message}"
                })
            else:
                # Add normal tool result to chat
                chat_history.append({
                    "role": "assistant",
                    "content": accumulated_response
                })
                chat_history.append({
                    "role": "user",
                    "content": f"Tool result: {json.dumps(tool_result)}"
                })
        except Exception as e:
            # Handle other errors silently to avoid disrupting the flow
            pass

    async def process_agent_message(self, prompt: str, session_id: str, job_name: str = None) -> AsyncGenerator[str, None]:
        """Process prompt through agent loop with tool execution and session context"""

        # Get the chat history context for the AI
        chat_history = self._setup_chat_history(prompt, session_id)

        iteration = 0
        max_iterations = 50 # Arbitrary for now
        tool_results_used = []

        while iteration < max_iterations:
            iteration += 1

            # Add spacing between agent loops (except for first iteration)
            if iteration > 1:
                yield json.dumps({
                    "type": "agent_process",
                    "content": "\n"
                })

            # Format reinforcement every iteration to prevent context dilution
            if iteration > 3:
                chat_history.append({
                    "role": "system",
                    "content": "REMEMBER: JSON format only - {'thought': '...', 'action': {...}} or {'thought': '...', 'finish': '...'}. CRITICAL: NEVER use 'finish' as an action name in Tools format!"
                })

            # Process AI stream
            accumulated_response = ""
            finish_found = False
            action_streamed = False

            async for result in self._process_ai_stream(chat_history):
                # We are still streaming
                if isinstance(result, str):
                    yield result
                # Done streaming
                else:
                    accumulated_response, finish_found, action_streamed, final_answer = result # Take important bits from AI output

            # If we found a final answer during streaming, break out of the main loop
            if finish_found:
                final_answer = accumulated_response
                break

            # If action was found, execute it and continue to next iteration
            if action_streamed:
                self._handle_tool_execution(accumulated_response, chat_history, tool_results_used, job_name)
                continue

            # If no finish or action found, treat as direct answer
            final_answer = accumulated_response
            yield json.dumps({
                "type": "final_answer",
                "content": final_answer
            })

        else:
            # Max iterations reached
            if not final_answer:
                final_answer = "\n\nI've reached the maximum number of steps. Please try a more specific question."
            else:
                final_answer += "\n\nI've reached the maximum number of steps. Please try a more specific question."
            yield final_answer

        # Add assistant message and store agent loop in session
        if final_answer:
            session_manager.add_agent_loop(session_id, prompt, final_answer)


# Global instance
agent_service = AgentService()