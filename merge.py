from __future__ import annotations

from mdac_bot.models import UnifiedData


def merge_data(base: UnifiedData, incoming: UnifiedData) -> UnifiedData:
    out = UnifiedData.from_json_dict(base.to_json_dict())

    def set_if_missing(obj, field: str, value):
        if value is None:
            return
        if getattr(obj, field) in (None, ""):
            setattr(obj, field, value)

    for field in ["full_name", "passport_number", "date_of_birth", "sex", "nationality_code", "place_of_birth_code", "passport_expiry"]:
        set_if_missing(out.person, field, getattr(incoming.person, field))

    for field in ["email", "phone_country_code", "phone_number"]:
        set_if_missing(out.contact, field, getattr(incoming.contact, field))

    for field in ["arrival_date", "departure_date", "travel_mode", "vessel_name", "embark_country_code"]:
        set_if_missing(out.trip, field, getattr(incoming.trip, field))

    for field in ["stay_type", "address1", "address2", "state_code", "postcode", "city_text"]:
        set_if_missing(out.accommodation, field, getattr(incoming.accommodation, field))

    return out
