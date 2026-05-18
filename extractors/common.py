from __future__ import annotations

import re
from datetime import date, datetime


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse_date_flexible(s: str) -> date | None:
    s = (s or "").strip()
    if not s:
        return None

    try:
        from dateutil import parser as date_parser

        dt = date_parser.parse(s, dayfirst=True, fuzzy=True)
        return dt.date()
    except Exception:
        pass

    cleaned = re.sub(r"[,\|]", " ", s)
    cleaned = normalize_spaces(cleaned)

    fmts = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
    ]

    for fmt in fmts:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    m = re.search(r"(\d{1,2})[.\s-](\d{1,2})[.\s-](\d{2,4})", cleaned)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y = 2000 + y if y <= (date.today().year % 100) + 5 else 1900 + y
        try:
            return date(y, mo, d)
        except ValueError:
            return None

    return None


def parse_mrz_date_yyMMdd(yyMMdd: str, *, for_expiry: bool) -> date | None:
    yyMMdd = re.sub(r"[^0-9]", "", yyMMdd or "")
    if len(yyMMdd) != 6:
        return None

    yy = int(yyMMdd[0:2])
    mm = int(yyMMdd[2:4])
    dd = int(yyMMdd[4:6])

    current_year = date.today().year % 100
    if for_expiry:
        century = 2000 if yy <= current_year + 20 else 1900
    else:
        century = 1900 if yy > current_year else 2000

    try:
        return date(century + yy, mm, dd)
    except ValueError:
        return None


def sex_to_mdac(value: str | None) -> str | None:
    v = (value or "").strip().upper()
    if v in {"M", "MALE", "1"}:
        return "1"
    if v in {"F", "FEMALE", "2"}:
        return "2"
    return None
