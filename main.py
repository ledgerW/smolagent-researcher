import os
import requests
from typing import Union, Dict, Annotated
from pydantic import BaseModel
from fastapi import FastAPI

from agent import manager_agent


class TaskInput(BaseModel):
    task: Annotated[str, ..., "The task to be performed"]

class TaskOutput(BaseModel):
    output: Annotated[str, ..., "The result of the task"]


app = FastAPI(title='Research Agents', version='0.1.0')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/ai_policy_agent", response_model=TaskOutput)
def ai_policy_agent(input: TaskInput) -> TaskOutput:
    return TaskOutput(output=manager_agent.run(input.task))

    #requests.post(
    #    os.getenv("MAKE_AI_POLICY_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}


@app.post("/ai_technical_agent", response_model=TaskOutput)
def ai_technical_agent(input: TaskInput) -> TaskOutput:
    return TaskOutput(output=manager_agent.run(input.task))

    #requests.post(
    #    os.getenv("MAKE_AI_TECHNICAL_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}


@app.post("/global_macroeconomic_agent", response_model=TaskOutput)
def global_macroeconomic_agent(input: TaskInput) -> TaskOutput:
    return TaskOutput(output=manager_agent.run(input.task))

    #requests.post(
    #    os.getenv("MAKE_GLOBAL_MACROECONOMIC_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}
