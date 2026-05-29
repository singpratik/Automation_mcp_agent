import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PromptClassifier:
    """Enhanced prompt classification with better intent detection"""
    
    # Extended keyword mappings
    BROWSER_KEYWORDS = [
        "open", "click", "navigate", "login", "upload", "tab", "screenshot",
        "scroll", "hover", "type", "submit", "search", "find", "wait",
        "browser", "webpage", "website", "page", "link", "button", "form"
    ]
    
    API_KEYWORDS = [
        "request", "api", "endpoint", "get", "post", "put", "delete", "patch",
        "http", "fetch", "call", "rest", "json", "response", "status", "header"
    ]
    
    DB_KEYWORDS = [
        "select", "insert", "update", "delete", "database", "query",
        "table", "column", "row", "join", "where", "sql", "db"
    ]
    
    FILE_KEYWORDS = [
        "read", "write", "create", "delete", "file", "directory", "path",
        "upload", "download", "save", "load", "open", "close"
    ]

    @staticmethod
    def score_keywords(text: str, keywords: list) -> float:
        """Score text based on keyword presence"""
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches / len(keywords) if keywords else 0

    @staticmethod
    def is_structured_request(text: str) -> bool:
        """Detect structured/JSON requests"""
        try:
            json.loads(text)
            return True
        except:
            pass
        
        # Check for structured patterns
        structured_patterns = [
            r'\{.*\}',  # JSON-like
            r'\[.*\]',  # Array-like
            r'^\w+\.\w+',  # Dot notation
        ]
        return any(re.search(pattern, text) for pattern in structured_patterns)


def parse_prompt_for_action(user_input: str) -> Dict[str, Any]:
    """
    Enhanced prompt parser with better intent detection and reliability
    
    Args:
        user_input: Natural language prompt from user
        
    Returns:
        Dictionary with intent classification and confidence scores
    """
    try:
        if not user_input or not isinstance(user_input, str):
            logger.warning(f"Invalid input: {type(user_input)}")
            return {
                "is_url": False,
                "is_sql": False,
                "is_browser_action": False,
                "llm_intent": "none",
                "should_act": False,
                "reason": "Invalid input",
                "confidence": 0
            }
        
        user_input = user_input.strip()
        
        # Rule-based checks
        is_url = bool(re.search(r'https?://|www\.', user_input))
        is_sql = bool(re.search(r'\b(select|insert|update|delete|from|where)\b', user_input, re.IGNORECASE))
        is_json = PromptClassifier.is_structured_request(user_input)
        
        # Keyword-based scoring
        browser_score = PromptClassifier.score_keywords(user_input, PromptClassifier.BROWSER_KEYWORDS)
        api_score = PromptClassifier.score_keywords(user_input, PromptClassifier.API_KEYWORDS)
        db_score = PromptClassifier.score_keywords(user_input, PromptClassifier.DB_KEYWORDS)
        file_score = PromptClassifier.score_keywords(user_input, PromptClassifier.FILE_KEYWORDS)
        
        # Determine primary intent from scores
        intent_scores = {
            "browser": browser_score,
            "api": api_score,
            "db": db_score,
            "file": file_score,
            "none": 0
        }
        
        primary_intent = max(intent_scores, key=intent_scores.get)
        primary_confidence = intent_scores[primary_intent]
        
        # Override with explicit patterns
        if is_sql:
            primary_intent = "db"
            primary_confidence = 0.95
        elif is_json:
            primary_intent = "api"
            primary_confidence = 0.9
        
        # LLM-based intent detection for ambiguous cases
        llm_intent = primary_intent
        llm_confidence = primary_confidence
        
        try:
            if primary_confidence < 0.6:  # Only call LLM for low-confidence cases
                from llm.llm_interface import get_llm_response
                
                llm_prompt = (
                    f"Classify this prompt for agentic action. "
                    f"Return JSON only: {{'intent': 'browser'/'api'/'db'/'file'/'none', 'confidence': 0.0-1.0}}. "
                    f"Prompt: '{user_input}'"
                )
                
                llm_response = get_llm_response(llm_prompt)
                
                # Try to parse LLM response
                try:
                    llm_result = json.loads(llm_response)
                    llm_intent = llm_result.get("intent", primary_intent)
                    llm_confidence = min(llm_result.get("confidence", 0.5), 0.95)
                except:
                    logger.debug(f"Failed to parse LLM response: {llm_response}")
                    llm_intent = primary_intent
                    llm_confidence = primary_confidence
        except ImportError:
            logger.debug("LLM interface not available, using rule-based classification only")
        
        # Determine if we should act
        should_act = (is_url and browser_score > 0.3) or is_sql or llm_intent in ["browser", "api", "db", "file"]
        
        result = {
            "is_url": is_url,
            "is_sql": is_sql,
            "is_browser_action": is_url and browser_score > 0.3,
            "llm_intent": llm_intent,
            "should_act": should_act,
            "reason": f"{llm_intent.upper()} action detected",
            "confidence": llm_confidence,
            "primary_intent": primary_intent,
            "intent_scores": intent_scores,
            "is_structured": is_json
        }
        
        logger.debug(f"Parsed prompt: intent={llm_intent}, confidence={llm_confidence:.2f}, should_act={should_act}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in parse_prompt_for_action: {e}", exc_info=True)
        return {
            "is_url": False,
            "is_sql": False,
            "is_browser_action": False,
            "llm_intent": "none",
            "should_act": False,
            "reason": f"Parser error: {str(e)}",
            "confidence": 0
        }
