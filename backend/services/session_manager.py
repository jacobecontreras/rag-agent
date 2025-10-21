import time
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class SessionContext:
    session_id: str
    agent_loops: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        self.max_agent_loops = 3

    def get_session(self, session_id: str) -> SessionContext:
        """Get or create session context"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id=session_id)

        session = self.sessions[session_id]
        session.last_updated = time.time()
        return session


    def add_agent_loop(self, session_id: str, user_message: str, final_answer: str):
        """Add completed agent loop to history with sliding window"""
        session = self.get_session(session_id)

        loop_data = {
            "user_message": user_message,
            "final_answer": final_answer,
            "timestamp": time.time()
        }

        # Add to loops and maintain sliding window
        session.agent_loops.append(loop_data)
        if len(session.agent_loops) > self.max_agent_loops:
            session.agent_loops.pop(0)  # Remove oldest


    def get_context_for_ai(self, session_id: str) -> List[Dict[str, str]]:
        """Get formatted context for AI consumption - last 3 loops only"""
        session = self.get_session(session_id)
        context = []

        # Add recent agent loops (3-loop sliding window)
        for loop in session.agent_loops:
            context.append({
                "role": "user",
                "content": f"Previous question: {loop['user_message']}"
            })
            context.append({
                "role": "assistant",
                "content": f"Previous analysis: {loop['final_answer']}"
            })

        return context


# Global instance
session_manager = SessionManager()