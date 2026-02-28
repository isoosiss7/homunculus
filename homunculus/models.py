from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AskHuman(BaseModel):
    question: str = Field(..., min_length=1)


class Done(BaseModel):
    summary: str = Field(..., min_length=1)
    result_json: dict[str, Any] | None = None
