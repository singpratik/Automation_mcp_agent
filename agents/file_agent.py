import os
import shutil
from pathlib import Path

class FileAgent:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def run(self, prompt: str) -> dict:
        task = self._parse_prompt(prompt)
        return self._handle(task)

    def _parse_prompt(self, prompt: str) -> dict:
        """
        Parses prompts like:
        'command=list path=./files' or 'command=copy path=a.txt destination=b.txt'
        """
        if not prompt or not prompt.strip():
            return {}
        
        task = {}
        parts = prompt.split()
        for part in parts:
            if '=' in part and len(part.split('=', 1)) == 2:
                key, value = part.split('=', 1)
                task[key.strip()] = value.strip()
        return task

    def _handle(self, task: dict) -> dict:
        command = task.get("command")
        path = task.get("path")

        if not command or not path:
            return {"error": "Missing 'command' or 'path' in prompt."}

        # Validate and sanitize paths to prevent path traversal
        safe_path = self._validate_path(path)
        if not safe_path:
            return {"error": "Invalid or unsafe path detected."}

        try:
            if command == "list":
                if not os.path.isdir(safe_path):
                    return {"error": "Path is not a directory."}
                return {"files": os.listdir(safe_path)}
            elif command == "delete":
                if not os.path.exists(safe_path):
                    return {"error": "File does not exist."}
                os.remove(safe_path)
                return {"status": "deleted"}
            elif command == "copy":
                dest = task.get("destination")
                if not dest:
                    return {"error": "Missing destination path."}
                safe_dest = self._validate_path(dest)
                if not safe_dest:
                    return {"error": "Invalid or unsafe destination path."}
                if not os.path.exists(safe_path):
                    return {"error": "Source file does not exist."}
                shutil.copy(safe_path, safe_dest)
                return {"status": "copied"}
            else:
                return {"error": f"Unknown command: {command}"}
        except FileNotFoundError:
            return {"error": "File or directory not found."}
        except PermissionError:
            return {"error": "Permission denied."}
        except OSError as e:
            return {"error": f"OS error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _validate_path(self, path: str) -> str:
        """Validate and sanitize file paths to prevent path traversal"""
        try:
            # Convert to Path object and resolve
            p = Path(path).resolve()
            
            # Define allowed base directory (current working directory)
            base_dir = Path.cwd().resolve()
            
            # Check if the resolved path is within the base directory
            if not str(p).startswith(str(base_dir)):
                return None
            
            # Additional checks for dangerous patterns
            path_str = str(p)
            dangerous_patterns = ['..', '~', '/etc', '/usr', '/var', '/sys', '/proc']
            if any(pattern in path_str for pattern in dangerous_patterns):
                return None
                
            return str(p)
        except Exception:
            return None
