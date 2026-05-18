from __future__ import annotations

from datetime import date


def format_ddmmyyyy(d: date | None) -> str | None:
    if not d:
        return None
    return d.strftime("%d/%m/%Y")

