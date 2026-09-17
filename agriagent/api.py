from __future__ import annotations

from importlib.resources import files

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import __version__
from .orchestrator import AgriAgent

app = FastAPI(
    title="AgriAgent Nepal",
    description="Chat-only deterministic multi-agent agronomy advisory reference implementation.",
    version=__version__,
)
agent = AgriAgent()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    debug: bool = False


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return files("agriagent.static").joinpath("index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    return agent.chat(req.message, debug=req.debug)
