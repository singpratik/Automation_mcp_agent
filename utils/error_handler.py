"""
Enhanced error handling utilities
Provides consistent error handling and recovery across agents
"""

import logging
import traceback
from typing import Callable, TypeVar, Optional, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

T = TypeVar('T')


class AgentError(Exception):
    """Base exception for agent errors"""
    pass


class BrowserError(AgentError):
    """Browser automation errors"""
    pass


class APIError(AgentError):
    """API testing errors"""
    pass


class DatabaseError(AgentError):
    """Database operation errors"""
    pass


class RetryConfig:
    """Retry configuration for resilient operations"""
    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0, 
                 initial_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay
        self.max_delay = max_delay


def retry_with_backoff(config: Optional[RetryConfig] = None) -> Callable:
    """
    Decorator for retrying operations with exponential backoff
    
    Args:
        config: Retry configuration (uses defaults if None)
        
    Returns:
        Decorated function with retry logic
    """
    config = config or RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = config.initial_delay
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{config.max_attempts}: {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} failed: {str(e)}")
                    
                    if attempt < config.max_attempts:
                        # Calculate delay with cap
                        actual_delay = min(delay, config.max_delay)
                        logger.info(f"Retrying in {actual_delay:.1f}s...")
                        time.sleep(actual_delay)
                        delay *= config.backoff_factor
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed")
            
            # All retries failed
            raise last_exception or AgentError(f"Operation failed after {config.max_attempts} attempts")
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling and logging"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "Operation", 
                    reraise: bool = False, fallback: Optional[Any] = None) -> Any:
        """
        Handle an error with logging and optional recovery
        
        Args:
            error: The exception to handle
            context: Context string for logging
            reraise: Whether to reraise the exception
            fallback: Fallback value to return if not reraising
            
        Returns:
            Fallback value or None
            
        Raises:
            Exception: If reraise is True
        """
        error_msg = f"❌ {context} failed: {str(error)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        if reraise:
            raise
        
        return fallback
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, param_name: str) -> bool:
        """
        Validate input parameter
        
        Args:
            value: Value to validate
            expected_type: Expected type
            param_name: Parameter name for error messages
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, expected_type):
            raise ValueError(f"{param_name} must be {expected_type.__name__}, got {type(value).__name__}")
        return True
    
    @staticmethod
    def safe_parse_json(json_str: str, default: Optional[dict] = None) -> dict:
        """Safely parse JSON with fallback"""
        import json
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return default or {}


def log_execution(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log function execution with timing
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        func_name = func.__name__
        logger.info(f"▶️  Executing {func_name}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"✅ {func_name} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {func_name} failed after {elapsed:.2f}s: {str(e)}")
            raise
    
    return wrapper
