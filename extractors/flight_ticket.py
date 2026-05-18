from __future__ import annotations

import re
from dataclasses import dataclass

from mdac_bot.extractors.common import parse_date_flexible
from mdac_bot.models import UnifiedData


@dataclass(frozen=True)
class TicketExtraction:
    data: UnifiedData
    confidence: float


def extract_ticket(text: str) -> TicketExtraction:
    data = UnifiedData()
    t = text or ""
    tu = t.upper()

    flight = None
    m = re.search(r"\b([A-Z]{2})\s?(\d{3,4})\b", tu)
    if m:
        flight = f"{m.group(1)}{m.group(2)}"
    if flight:
        data.trip.vessel_name = flight
        data.trip.travel_mode = "1"

    date_candidates: list[str] = []
    for pat in [
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        r"\b(\d{1,2}\s+[A-Z]{3,9}\s+\d{2,4})\b",
        r"\b([A-Z]{3,9}\s+\d{1,2},?\s+\d{2,4})\b",
    ]:
        date_candidates.extend(re.findall(pat, tu))

    parsed = [parse_date_flexible(x) for x in date_candidates]
    parsed = [d for d in parsed if d]
    parsed = sorted(set(parsed))

    if parsed:
        data.trip.arrival_date = parsed[0]
        if len(parsed) > 1:
            data.trip.departure_date = parsed[-1]

    conf = 0.2
    if data.trip.vessel_name:
        conf += 0.3
    if data.trip.arrival_date:
        conf += 0.3

    return TicketExtraction(data=data, confidence=min(conf, 0.8))

