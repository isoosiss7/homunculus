from __future__ import annotations

from typing import Self
from urllib.parse import quote, unquote

from pydantic import BaseModel


class RoleRef(BaseModel):
    role: str
    name: str
    nth: int = 0

    def to_str(self) -> str:
        encoded_name = quote(self.name, safe="")
        return f"role:{self.role};name:{encoded_name};nth:{self.nth}"

    @classmethod
    def from_str(cls, value: str) -> Self:
        parts = value.split(";")
        data: dict[str, str] = {}
        for part in parts:
            if not part:
                continue
            if ":" not in part:
                raise ValueError(f"Invalid role ref part: {part!r}")
            key, part_value = part.split(":", 1)
            data[key] = part_value

        role = data.get("role")
        name = data.get("name")
        nth_raw = data.get("nth")

        if role is None or name is None or nth_raw is None:
            raise ValueError(f"Invalid role ref: {value!r}")

        try:
            nth = int(nth_raw)
        except ValueError as exc:
            raise ValueError(f"Invalid role ref nth: {nth_raw!r}") from exc

        return cls(role=role, name=unquote(name), nth=nth)
