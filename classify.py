from __future__ import annotations

import re


def classify_document(text: str) -> str:
    t = (text or "").upper()

    mrz_like = any("<<" in line and len(line.strip()) >= 30 for line in t.splitlines())
    if mrz_like or "P<" in t:
        return "passport"

    if "HOTEL" in t or "BOOKING" in t or "RESERVATION" in t or "CHECK-IN" in t:
        return "hotel"

    if "BOARDING PASS" in t or "E-TICKET" in t or "ETICKET" in t:
        return "ticket"

    if re.search(r"\b[A-Z]{2}\s?\d{3,4}\b", t):
        return "ticket"

    return "unknown"

