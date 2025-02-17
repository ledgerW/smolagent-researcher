import os
import requests
from typing import Union, Dict

from fastapi import FastAPI

from agent import manager_agent


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/ai_policy_agent")
def ai_policy_agent(task: str) -> Dict[str, str]:
    return manager_agent.run(task)

    #requests.post(
    #    os.getenv("MAKE_AI_POLICY_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}


@app.post("/ai_technical_agent")
def ai_technical_agent(task: str) -> Dict[str, str]:
    return manager_agent.run(task)

    #requests.post(
    #    os.getenv("MAKE_AI_TECHNICAL_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}


@app.post("/global_macroeconomic_agent")
def global_macroeconomic_agent(task: str) -> Dict[str, str]:
    return manager_agent.run(task)

    #requests.post(
    #    os.getenv("MAKE_GLOBAL_MACROECONOMIC_HOOK"),
    #    json={"result": res}
    #)
    #return {"result": res}
