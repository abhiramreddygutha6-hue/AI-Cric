import json
import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat_tools import TOOLS, run_tool

router = APIRouter(tags=["chat"])

SYSTEM = """You are AiCric, a cricket analyst helping a coach prepare for matches and tournaments.
Rules:
- Every number you state must come from a tool result. Never recall or estimate statistics yourself.
- Use find_player first to get player ids. If a name is ambiguous, ask which player is meant.
- The data only covers matches imported into this system, so mention small samples (under about 60 balls) as unreliable.
- Efficiency scores are percentile based and relative to other qualified players, not absolute.
- For planning questions (who should bowl when, weaknesses, matchups), give a clear recommendation, say which stats it rests on, and say what the data cannot show.
- Reply in short plain text. No markdown headings or bold; simple hyphen lists are fine."""


class Msg(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatIn(BaseModel):
    messages: list[Msg] = Field(min_length=1, max_length=30)


@router.post("/chat")
def chat(body: ChatIn, db: Session = Depends(get_db)):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise HTTPException(503, "The assistant needs an ANTHROPIC_API_KEY. Set it in the terminal that runs the backend, then restart the backend.")
    try:
        import anthropic
    except ImportError:
        raise HTTPException(503, "The 'anthropic' package is not installed. Run: python -m pip install anthropic")

    client = anthropic.Anthropic(api_key=key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    used = []
    for _ in range(6):  # at most 6 rounds of tool use
        try:
            resp = client.messages.create(model=model, max_tokens=1200, system=SYSTEM, tools=TOOLS, messages=messages)
        except anthropic.APIError as e:
            raise HTTPException(502, f"The AI service returned an error: {e}")
        if resp.stop_reason != "tool_use":
            return {"reply": "".join(b.text for b in resp.content if b.type == "text"), "tools_used": used}
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                used.append(b.name)
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": json.dumps(run_tool(db, b.name, b.input), default=str)})
        messages.append({"role": "user", "content": results})
    return {"reply": "I could not finish looking that up. Try a more specific question.", "tools_used": used}
