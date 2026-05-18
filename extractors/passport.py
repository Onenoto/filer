from __future__ import annotations

import re
from dataclasses import dataclass

from mdac_bot.extractors.common import normalize_spaces, parse_mrz_date_yyMMdd, sex_to_mdac
from mdac_bot.models import UnifiedData


@dataclass(frozen=True)
class PassportExtraction:
    data: UnifiedData
    confidence: float


def _find_mrz_lines(text: str) -> tuple[str, str] | None:
    lines = [re.sub(r"\s+", "", l.strip().upper()) for l in (text or "").splitlines() if l.strip()]
    lines = [l for l in lines if "<<" in l and len(l) >= 30]
    if len(lines) < 2:
        return None

    candidates = []
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if len(a) >= 40 and len(b) >= 40:
            candidates.append((a, b))
    if not candidates:
        return None

    a, b = max(candidates, key=lambda x: min(len(x[0]), len(x[1])))
    a = (a + "<" * 44)[:44]
    b = (b + "<" * 44)[:44]
    return a, b


def _parse_td3(mrz1: str, mrz2: str) -> UnifiedData:
    data = UnifiedData()

    if mrz1.startswith("P<") and len(mrz1) >= 5:
        data.person.nationality_code = mrz2[10:13].replace("<", "") or None

    names_raw = mrz1[5:].split("<<", 1)[0:2]
    surname = names_raw[0].replace("<", " ").strip()
    given = (names_raw[1] if len(names_raw) > 1 else "").replace("<", " ").strip()
    full = normalize_spaces(" ".join([surname, given]).strip())
    data.person.full_name = full or None

    passport_number = mrz2[0:9].replace("<", "").strip()
    data.person.passport_number = passport_number or None

    dob = parse_mrz_date_yyMMdd(mrz2[13:19], for_expiry=False)
    data.person.date_of_birth = dob

    sex = mrz2[20:21]
    data.person.sex = sex_to_mdac(sex)

    exp = parse_mrz_date_yyMMdd(mrz2[21:27], for_expiry=True)
    data.person.passport_expiry = exp

    return data


def extract_passport(text: str) -> PassportExtraction:
    mrz = _find_mrz_lines(text)
    if mrz:
        mrz1, mrz2 = mrz
        data = _parse_td3(mrz1, mrz2)
        return PassportExtraction(data=data, confidence=0.85)

    data = UnifiedData()
    t = text or ""

    m = re.search(r"\bPASSPORT\s*NO\.?\s*[:#]?\s*([A-Z0-9<]{6,12})\b", t, re.I)
    if m:
        data.person.passport_number = m.group(1).replace("<", "").strip()

    return PassportExtraction(data=data, confidence=0.25)

