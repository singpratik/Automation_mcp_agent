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
        'query="SELECT * FROM users" db_path=mydb.sqlite'
        """
        if not prompt or not prompt.strip():
            return {}
        
        task = {}
        # Better parsing that handles quoted values
        import re
        pattern = r'(\w+)=(?:"([^"]*)"|([^\s]+))'
        matches = re.findall(pattern, prompt)
        for match in matches:
            key = match[0]
            value = match[1] if match[1] else match[2]
            task[key.strip()] = value.strip()
        return task

    def _handle(self, task: dict) -> dict:
        query = task.get("query")
        db_path = task.get("db_path", "test.db")

        if not query:
            return {"error": "Missing SQL query."}

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if query.strip().lower().startswith("select"):
                    rows = cursor.fetchall()
                    result = {"rows": rows}
                else:
                    conn.commit()
                    result = {"status": "Query executed"}
                return result
        except sqlite3.Error as e:
            return {"error": f"Database error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def run_db_tests(self, db_tests):
        """
        Run a list of DB test prompts and return their results.
        Each test in db_tests should be a string prompt describing the DB operation.
        """
        results = []
        for test in db_tests:
            result = self.run(test)
            results.append({"test": test, "result": result})
        return results
