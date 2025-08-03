
from fastapi import FastAPI, Request
from agents import browser_agent, api_agent, sql_agent, file_agent
from llm.llm_interface import prompt_llm

app = FastAPI(title="MCP AI Agent", description="Multi-Agent Task Orchestrator", version="1.0")

@app.get("/")
async def root():
    return {"status": "MCP AI Agent is running"}

@app.post("/task/")
async def run_task(task: dict):
    task_type = task.get("type")
    if task_type == "browser":
        return browser_agent.handle(task)
    elif task_type == "api":
        return api_agent.handle(task)
    elif task_type == "sql":
        return sql_agent.handle(task)
    elif task_type == "file":
        return file_agent.handle(task)
    else:
        return {"error": "Unknown task type"}

@app.post("/prompt/")
async def convert_prompt(prompt: dict):
    user_prompt = prompt.get("prompt", "")
    model = prompt.get("model", "llama3")
    temp = prompt.get("temperature", 0.7)
    formatted = f"""Convert this natural instruction into a structured JSON task for the MCP agent system:

'{user_prompt}'

Return JSON with 'type', 'action' and other needed fields."""
    response = prompt_llm(formatted, model=model, temperature=temp)
    return {"task": response}
