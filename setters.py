from __future__ import annotations

from datetime import date

from mdac_bot.extractors.common import parse_date_flexible, sex_to_mdac
from mdac_bot.models import UnifiedData


def set_field(data: UnifiedData, path: str, value: str) -> None:
    path = (path or "").strip()
    value = (value or "").strip()
    if not path or "." not in path:
        raise ValueError("path must be like person.full_name")

    root, field = path.split(".", 1)
    if root not in {"person", "contact", "trip", "accommodation"}:
        raise ValueError("unknown root")

    obj = getattr(data, root)

    if root == "person" and field in {"date_of_birth", "passport_expiry"}:
        d = parse_date_flexible(value)
        if not d:
            raise ValueError("cannot parse date")
        setattr(obj, field, d)
        return

    if root == "trip" and field in {"arrival_date", "departure_date"}:
        d = parse_date_flexible(value)
        if not d:
            raise ValueError("cannot parse date")
        setattr(obj, field, d)
        return

    if root == "person" and field == "sex":
        s = sex_to_mdac(value)
        if not s:
            raise ValueError("sex must be M/F")
        setattr(obj, field, s)
        return

    if not hasattr(obj, field):
        raise ValueError("unknown field")

    setattr(obj, field, value)

