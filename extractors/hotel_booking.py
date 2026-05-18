from __future__ import annotations

import re
from dataclasses import dataclass

from mdac_bot.extractors.common import normalize_spaces
from mdac_bot.models import UnifiedData


_STATE_TO_CODE = {
    "JOHOR": "01",
    "KEDAH": "02",
    "KELANTAN": "03",
    "MELAKA": "04",
    "MALACCA": "04",
    "NEGERI SEMBILAN": "05",
    "PAHANG": "06",
    "PULAU PINANG": "07",
    "PENANG": "07",
    "PERAK": "08",
    "PERLIS": "09",
    "SELANGOR": "10",
    "TERENGGANU": "11",
    "SABAH": "12",
    "SARAWAK": "13",
    "WP KUALA LUMPUR": "14",
    "KUALA LUMPUR": "14",
    "WP LABUAN": "15",
    "LABUAN": "15",
    "WP PUTRAJAYA": "16",
    "PUTRAJAYA": "16",
}


@dataclass(frozen=True)
class HotelExtraction:
    data: UnifiedData
    confidence: float


def extract_hotel_booking(text: str) -> HotelExtraction:
    data = UnifiedData()
    data.accommodation.stay_type = "01"

    lines = [normalize_spaces(l) for l in (text or "").splitlines()]
    lines = [l for l in lines if l]
    joined = " | ".join(lines).upper()

    postcode = None
    m = re.search(r"\b(\d{5})\b", joined)
    if m:
        postcode = m.group(1)
        data.accommodation.postcode = postcode

    state_code = None
    state_text = None
    for st, code in _STATE_TO_CODE.items():
        if st in joined:
            state_code = code
            state_text = st
            break
    data.accommodation.state_code = state_code

    addr = None
    for i, l in enumerate(lines):
        if re.search(r"\bADDRESS\b", l, re.I):
            tail = [x for x in lines[i + 1 : i + 5] if x]
            addr = ", ".join(tail).strip(", ")
            break
    if not addr:
        candidates = [l for l in lines if any(k in l.upper() for k in ["STREET", "ROAD", "JALAN", "NO.", "LOT", "BUILDING", "KUALA LUMPUR"])]
        if candidates:
            addr = candidates[0]

    if addr:
        addr = normalize_spaces(addr)
        data.accommodation.address1 = addr[:120]

    city = None
    if state_text and "KUALA LUMPUR" in joined:
        city = "KUALA LUMPUR"
    else:
        m = re.search(r"\b([A-Z][A-Z ]{2,})\b", " ".join(lines), re.I)
        if m:
            city = normalize_spaces(m.group(1)).upper()
    if city:
        data.accommodation.city_text = city

    conf = 0.2
    if data.accommodation.address1:
        conf += 0.3
    if data.accommodation.state_code:
        conf += 0.2
    if data.accommodation.postcode:
        conf += 0.2

    return HotelExtraction(data=data, confidence=min(conf, 0.8))

