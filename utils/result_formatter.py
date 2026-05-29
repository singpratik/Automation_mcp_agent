"""
Result formatting and rendering utilities for Streamlit
Converts agent results to HTML/Markdown for display
"""

import html
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def format_browser_result(result: Any) -> str:
    """Format browser automation result for display"""
    if result is None:
        return """
        <div style='background: #fef3c7; border-radius: 10px; padding: 20px; margin: 10px 0; border-left: 4px solid #f59e0b;'>
            <h4 style='color: #d97706; margin: 0;'>⚠️ No result returned from automation.</h4>
        </div>
        """
    
    result_str = str(result)
    
    # If it's already formatted HTML, return as-is
    if result_str.strip().startswith('<div') and 'style=' in result_str:
        return result_str
    
    # Otherwise, format it nicely
    return f"""
    <div style='background: #f8fafc; border-radius: 12px; padding: 24px; margin: 15px 0; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <h4 style='color: #1e40af; margin: 0 0 15px 0; display: flex; align-items: center; font-size: 18px; font-weight: 600;'>
            🤖 <span style='margin-left: 8px;'>Automation Result</span>
        </h4>
        <div style='background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;'>
            <pre style='margin: 0; color: #374151; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.6;'>{html.escape(result_str)}</pre>
        </div>
    </div>
    """


def format_status_badge(status: str) -> str:
    """Format status as a styled badge"""
    if status == "success":
        color = "#22c55e"
        bg_color = "#f0fdf4"
        icon = "✅"
    elif status == "error":
        color = "#ef4444"
        bg_color = "#fef2f2"
        icon = "❌"
    else:
        color = "#f59e0b"
        bg_color = "#fffbeb"
        icon = "⚠️"
    
    return f"""
    <span style='background: {bg_color}; color: {color}; padding: 6px 12px; 
    border-radius: 20px; font-weight: 600; font-size: 0.9rem;'>
    {icon} {status.upper()}
    </span>
    """


def format_stats_card(value: Any, label: str, color: str = "#3498db") -> str:
    """Format a single stat card"""
    return f"""
    <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border-radius: 15px; padding: 25px; text-align: center;
    border-left: 5px solid {color}; transition: transform 0.3s ease;'>
        <div style='font-size: 2.5rem; font-weight: 900; margin-bottom: 8px; color: {color};'>{value}</div>
        <div style='color: #7f8c8d; font-size: 1rem; text-transform: uppercase;
        font-weight: 600; letter-spacing: 0.5px;'>{label}</div>
    </div>
    """


def format_error_box(message: str, title: str = "Error") -> str:
    """Format error message in a styled box"""
    return f"""
    <div style='background: #fef2f2; border-radius: 12px; padding: 20px; 
    margin: 15px 0; border-left: 4px solid #ef4444;'>
        <h4 style='color: #dc2626; margin: 0 0 10px 0;'>❌ {title}</h4>
        <p style='color: #7f1d1d; margin: 0; white-space: pre-wrap;'>{html.escape(message)}</p>
    </div>
    """


def format_success_box(message: str, title: str = "Success") -> str:
    """Format success message in a styled box"""
    return f"""
    <div style='background: #f0fdf4; border-radius: 12px; padding: 20px; 
    margin: 15px 0; border-left: 4px solid #22c55e;'>
        <h4 style='color: #166534; margin: 0 0 10px 0;'>✅ {title}</h4>
        <p style='color: #166534; margin: 0; white-space: pre-wrap;'>{html.escape(message)}</p>
    </div>
    """


def truncate_text(text: str, max_length: int = 100) -> str:
    """Safely truncate text with ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


class ResultRenderer:
    """Unified result rendering for different agent types"""
    
    @staticmethod
    def render_browser_result(result: Dict[str, Any]) -> str:
        """Render browser automation result"""
        return format_browser_result(result.get("result", "No result"))
    
    @staticmethod
    def render_api_result(result: Dict[str, Any]) -> str:
        """Render API test result"""
        api_result = result.get("result", "No result")
        
        if isinstance(api_result, dict):
            return f"""
            <div style='background: #f8fafc; border-radius: 12px; padding: 20px;'>
                <h4>📊 API Test Result</h4>
                <pre style='background: white; padding: 15px; border-radius: 8px; 
                overflow-x: auto;'>{html.escape(str(api_result))}</pre>
            </div>
            """
        else:
            return format_browser_result(api_result)
    
    @staticmethod
    def render_db_result(result: Dict[str, Any]) -> str:
        """Render database query result"""
        db_result = result.get("result", "No result")
        
        return f"""
        <div style='background: #f8fafc; border-radius: 12px; padding: 20px;'>
            <h4>💾 Database Query Result</h4>
            <pre style='background: white; padding: 15px; border-radius: 8px; 
            overflow-x: auto; max-height: 400px;'>{html.escape(str(db_result))}</pre>
        </div>
        """
