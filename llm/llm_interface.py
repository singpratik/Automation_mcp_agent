import openai
import os
from datetime import datetime

def sanitize_prompt(prompt):
    """Basic prompt injection protection: blocks suspicious patterns."""
    forbidden_patterns = [
        "ignore previous instructions",
        "forget previous instructions",
        "you are now",
        "act as",
        "system:",
        "user:",
        "assistant:",
        "```",
        "import os",
        "openai.api_key",
        "os.environ",
        "run code",
        "execute",
        "shell",
        "bash",
        "python",
        "reset",
        "delete",
        "remove"
    ]
    lowered = prompt.lower()
    for pattern in forbidden_patterns:
        if pattern in lowered:
            return False, f"Prompt blocked due to forbidden pattern: '{pattern}'"
    return True, ""

def get_api_key():
    """Stub for secure API key retrieval. Replace with secrets manager integration."""
    api_key = os.getenv("OPENAI_API_KEY")
    # TODO: Integrate with a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)
    return api_key

def get_llm_response(prompt):
    """Get response from OpenAI for non-browser tasks with prompt injection protection and secure API key management."""
    is_safe, reason = sanitize_prompt(prompt)
    if not is_safe:
        return f"Error: {reason}"

    api_key = get_api_key()
    if not api_key:
        return "Error: OpenAI API key not found in environment variables"
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. Provide concise and accurate responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except openai.AuthenticationError:
        return "Error: Invalid OpenAI API key"
    except openai.RateLimitError:
        return "Error: OpenAI API rate limit exceeded"
    except openai.APIError as e:
        return f"Error: OpenAI API error - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"
