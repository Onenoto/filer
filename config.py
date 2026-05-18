from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    data_dir: Path
    headless: bool
    tesseract_cmd: str | None


def load_config() -> Config:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    data_dir = Path(os.environ.get("DATA_DIR", "./data")).resolve()
    headless = os.environ.get("HEADLESS", "true").strip().lower() not in {"0", "false", "no"}
    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    tesseract_cmd = tesseract_cmd.strip() if tesseract_cmd else None

    data_dir.mkdir(parents=True, exist_ok=True)

    return Config(
        telegram_bot_token=token,
        data_dir=data_dir,
        headless=headless,
        tesseract_cmd=tesseract_cmd,
    )

