"""
Session management utilities for Streamlit app
Handles chat sessions, conversation history, and session persistence
"""

import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ChatSession:
    """Represents a single chat session with history"""
    
    def __init__(self, session_id: int, title: str, messages: Optional[List[Dict]] = None):
        self.id = session_id
        self.title = title
        self.messages = messages or []
        self.timestamp = datetime.datetime.now().strftime("%H:%M")
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.created_at = datetime.datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add a message to the session"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
    
    def get_summary(self) -> str:
        """Get a short summary of the session"""
        if self.messages:
            first_msg = next((m['content'] for m in self.messages if m['role'] == 'user'), "")
            return first_msg[:40] + "..." if len(first_msg) > 40 else first_msg
        return "Empty session"


class SessionManager:
    """Manages multiple chat sessions and conversation history"""
    
    def __init__(self):
        self.sessions: List[ChatSession] = []
        self.current_session_id: Optional[int] = None
        self.conversation_history: List[Dict] = []
        logger.info("SessionManager initialized")
    
    def create_session(self, messages: Optional[List[Dict]] = None) -> ChatSession:
        """Create a new chat session"""
        session_id = len(self.sessions)
        
        if messages:
            title = next(
                (m['content'][:40] for m in messages if m['role'] == 'user'),
                f"Chat {session_id}"
            )
        else:
            title = f"New Chat"
        
        session = ChatSession(session_id, title, messages or [])
        self.sessions.append(session)
        self.current_session_id = session_id
        
        logger.info(f"✅ Created new session (ID: {session_id}): {title}")
        return session
    
    def add_to_history(self, role: str, content: str):
        """Add message to current conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        if self.current_session_id is not None and self.current_session_id < len(self.sessions):
            return self.sessions[self.current_session_id]
        return None
    
    def switch_session(self, session_id: int) -> bool:
        """Switch to a different session"""
        if 0 <= session_id < len(self.sessions):
            self.current_session_id = session_id
            self.conversation_history = self.sessions[session_id].messages.copy()
            logger.info(f"✅ Switched to session {session_id}")
            return True
        logger.warning(f"Invalid session ID: {session_id}")
        return False
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        if 0 <= session_id < len(self.sessions):
            deleted = self.sessions.pop(session_id)
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.conversation_history = []
            logger.info(f"✅ Deleted session {session_id}")
            return True
        return False
    
    def search_sessions(self, query: str) -> List[ChatSession]:
        """Search sessions by title/content"""
        query_lower = query.lower()
        results = [s for s in self.sessions if query_lower in s.title.lower()]
        return results
    
    def get_all_sessions(self) -> List[ChatSession]:
        """Get all sessions in reverse chronological order"""
        return list(reversed(self.sessions))
    
    def save_session_to_history(self):
        """Save current conversation to session history"""
        if self.conversation_history:
            self.create_session(self.conversation_history.copy())
            logger.info("✅ Session saved to history")
    
    def clear_all(self):
        """Clear all sessions and history"""
        self.sessions = []
        self.conversation_history = []
        self.current_session_id = None
        logger.info("All sessions cleared")
