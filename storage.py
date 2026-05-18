from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mdac_bot.models import UnifiedData


@dataclass
class UserState:
    data: UnifiedData
    ocr_texts: dict[str, str]


class UserStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._users_dir = base_dir / "users"
        self._users_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: int) -> Path:
        return self._users_dir / f"{user_id}.json"

    def load(self, user_id: int) -> UserState:
        p = self._path(user_id)
        if not p.exists():
            return UserState(data=UnifiedData(), ocr_texts={})
        raw = json.loads(p.read_text(encoding="utf-8"))
        return UserState(
            data=UnifiedData.from_json_dict(raw.get("data") or {}),
            ocr_texts=raw.get("ocr_texts") or {},
        )

    def save(self, user_id: int, state: UserState) -> None:
        p = self._path(user_id)
        tmp = p.with_suffix(".json.tmp")
        payload: dict[str, Any] = {
            "data": state.data.to_json_dict(),
            "ocr_texts": state.ocr_texts,
        }
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(p)

    def reset(self, user_id: int) -> None:
        p = self._path(user_id)
        if p.exists():
            p.unlink()
