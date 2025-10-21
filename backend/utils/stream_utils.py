import json
from typing import List, NamedTuple


class StreamResult(NamedTuple):
    """Result of parsing a stream token"""
    outputs: List[str]
    accumulated: str
    finish_buffer: str
    streamed_fields: set
    is_complete: bool
    final_answer: str


def parse_stream_token(token: str, accumulated: str, finish_buffer: str,
                      streamed_fields: set) -> StreamResult:
    """Parse streaming token and return updated state"""
    accumulated += token
    finish_buffer += token
    outputs = []
    is_complete = False
    final_answer = ""

    # Parse complete JSON fields
    try:
        response_data = json.loads(accumulated)

        # Stream thought once
        if "thought" in response_data and "thought" not in streamed_fields:
            outputs.append(json.dumps({
                "type": "agent_process",
                "content": f"{response_data['thought']}\n\n"
            }))
            streamed_fields.add("thought")

        # Stream action once
        if "action" in response_data and "action" not in streamed_fields:
            action_data = response_data["action"]
            action_name = action_data.get("name", "unknown")
            input_data = action_data.get("input", {})
            input_display = str(input_data) if input_data else "{}"

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
        elif finish_content:
            outputs.append(json.dumps({
                "type": "final_answer_partial",
                "content": finish_content
            }))

    return StreamResult(outputs, accumulated, finish_buffer, streamed_fields, is_complete, final_answer)