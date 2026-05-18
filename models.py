from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass
class Person:
    full_name: str | None = None
    passport_number: str | None = None
    date_of_birth: date | None = None
    sex: str | None = None
    nationality_code: str | None = None
    place_of_birth_code: str | None = None
    passport_expiry: date | None = None


@dataclass
class Contact:
    email: str | None = None
    phone_country_code: str | None = None
    phone_number: str | None = None


@dataclass
class Trip:
    arrival_date: date | None = None
    departure_date: date | None = None
    travel_mode: str | None = None
    vessel_name: str | None = None
    embark_country_code: str | None = None


@dataclass
class Accommodation:
    stay_type: str | None = None
    address1: str | None = None
    address2: str | None = None
    state_code: str | None = None
    postcode: str | None = None
    city_text: str | None = None


@dataclass
class UnifiedData:
    person: Person = field(default_factory=Person)
    contact: Contact = field(default_factory=Contact)
    trip: Trip = field(default_factory=Trip)
    accommodation: Accommodation = field(default_factory=Accommodation)

    def to_json_dict(self) -> dict[str, Any]:
        def encode(v: Any) -> Any:
            if isinstance(v, date):
                return v.isoformat()
            if isinstance(v, list):
                return [encode(x) for x in v]
            if isinstance(v, dict):
                return {k: encode(x) for k, x in v.items()}
            return v

        return encode(asdict(self))

    @staticmethod
    def from_json_dict(d: dict[str, Any]) -> "UnifiedData":
        def parse_date(v: Any) -> date | None:
            if not v:
                return None
            if isinstance(v, date):
                return v
            return date.fromisoformat(v)

        person = d.get("person") or {}
        contact = d.get("contact") or {}
        trip = d.get("trip") or {}
        accommodation = d.get("accommodation") or {}

        return UnifiedData(
            person=Person(
                full_name=person.get("full_name"),
                passport_number=person.get("passport_number"),
                date_of_birth=parse_date(person.get("date_of_birth")),
                sex=person.get("sex"),
                nationality_code=person.get("nationality_code"),
                place_of_birth_code=person.get("place_of_birth_code"),
                passport_expiry=parse_date(person.get("passport_expiry")),
            ),
            contact=Contact(
                email=contact.get("email"),
                phone_country_code=contact.get("phone_country_code"),
                phone_number=contact.get("phone_number"),
            ),
            trip=Trip(
                arrival_date=parse_date(trip.get("arrival_date")),
                departure_date=parse_date(trip.get("departure_date")),
                travel_mode=trip.get("travel_mode"),
                vessel_name=trip.get("vessel_name"),
                embark_country_code=trip.get("embark_country_code"),
            ),
            accommodation=Accommodation(
                stay_type=accommodation.get("stay_type"),
                address1=accommodation.get("address1"),
                address2=accommodation.get("address2"),
                state_code=accommodation.get("state_code"),
                postcode=accommodation.get("postcode"),
                city_text=accommodation.get("city_text"),
            ),
        )

