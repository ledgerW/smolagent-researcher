from typing import Union

from fastapi import FastAPI

from agent import manager_agent

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/task_manager_agent")
def task_manager_agent(task: str) -> str:
    return manager_agent.run(task)