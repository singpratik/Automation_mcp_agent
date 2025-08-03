import os
import shutil

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
        task = {}
        parts = prompt.split()
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                task[key.strip()] = value.strip()
        return task

    def _handle(self, task: dict) -> dict:
        command = task.get("command")
        path = task.get("path")

        if not command or not path:
            return {"error": "Missing 'command' or 'path' in prompt."}

        try:
            if command == "list":
                return {"files": os.listdir(path)}
            elif command == "delete":
                os.remove(path)
                return {"status": "deleted"}
            elif command == "copy":
                dest = task.get("destination")
                if not dest:
                    return {"error": "Missing destination path."}
                shutil.copy(path, dest)
                return {"status": "copied"}
            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            return {"error": str(e)}
