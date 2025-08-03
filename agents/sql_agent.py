import sqlite3

class SQLAgent:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def run(self, prompt: str) -> dict:
        task = self._parse_prompt(prompt)
        return self._handle(task)

    def _parse_prompt(self, prompt: str) -> dict:
        """
        Parses prompts like:
        'query=SELECT * FROM users db_path=mydb.sqlite'
        """
        task = {}
        parts = prompt.split()
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                task[key.strip()] = value.strip()
        return task

    def _handle(self, task: dict) -> dict:
        query = task.get("query")
        db_path = task.get("db_path", "test.db")

        if not query:
            return {"error": "Missing SQL query."}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)

            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                result = {"rows": rows}
            else:
                conn.commit()
                result = {"status": "Query executed"}

            conn.close()
            return result
        except Exception as e:
            return {"error": str(e)}
