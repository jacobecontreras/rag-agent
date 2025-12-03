import json
from typing import List, NamedTuple
from tools import TOOLS


class StreamResult(NamedTuple):
    """Result of parsing a stream token"""
    outputs: List[str]
    accumulated: str
    finish_buffer: str
    streamed_fields: set
    is_complete: bool
    final_answer: str
    thought_buffer: dict


def parse_stream_token(token: str, accumulated: str, finish_buffer: str,
                      streamed_fields: set, thought_buffer: dict = None) -> StreamResult:
    """Parse streaming token and return updated state"""
    if thought_buffer is None:
        thought_buffer = {"has_thought": False, "thought_content": "", "thought_streamed": False}

    accumulated += token
    finish_buffer += token
    outputs = []
    is_complete = False
    final_answer = ""

    # Parse complete JSON fields
    try:
        response_data = json.loads(accumulated)

        # Store thought but don't stream yet
        if "thought" in response_data and not thought_buffer["thought_streamed"]:
            thought_buffer["has_thought"] = True
            thought_buffer["thought_content"] = response_data['thought']

        # Stream action once - also stream stored thought if it exists
        if "action" in response_data and "action" not in streamed_fields:
            action_data = response_data["action"]
            action_name = action_data.get("name", "unknown")
            input_data = action_data.get("input", {})
            input_display = str(input_data) if input_data else "{}"

            # Don't stream invalid tool calls, these are handled silently by error handling
            if action_name in TOOLS:
                # Stream thought first if we have one
                if thought_buffer["has_thought"] and not thought_buffer["thought_streamed"]:
                    outputs.append(json.dumps({
                        "type": "agent_process",
                        "content": f"{thought_buffer['thought_content']}\n\n"
                    }))
                    thought_buffer["thought_streamed"] = True

                # Stream action
                outputs.append(json.dumps({
                    "type": "agent_process",
                    "content": f"→ {action_name}({input_display})\n"
                }))
            streamed_fields.add("action")

    except json.JSONDecodeError:
        pass

    # Handle finish field streaming
    if '"finish": "' in finish_buffer:
        start_pos = finish_buffer.find('"finish": "') + 11
        finish_content = finish_buffer[start_pos:]

        # Find closing quote
        end_pos = -1
        for i in range(len(finish_content)):
            if finish_content[i] == '"' and (i == 0 or finish_content[i-1] != '\\'):
                end_pos = i
                break

        if end_pos != -1:
            final_answer = finish_content[:end_pos]
            outputs.append(json.dumps({
                "type": "final_answer",
                "content": final_answer
            }))
            is_complete = True

            # If we finish without an action, discard the thought (don't stream it)
            if thought_buffer["has_thought"] and not thought_buffer["thought_streamed"]:
                # Thought is discarded - no Agent Process will be shown
                pass

        elif finish_content:
            outputs.append(json.dumps({
                "type": "final_answer_partial",
                "content": finish_content
            }))

    # Add thought_buffer to StreamResult to persist across calls
    return StreamResult(outputs, accumulated, finish_buffer, streamed_fields, is_complete, final_answer, thought_buffer)