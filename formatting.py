from __future__ import annotations

from datetime import date

from mdac_bot.models import UnifiedData


def _d(d: date | None) -> str:
    return d.isoformat() if d else "-"


def format_profile(data: UnifiedData) -> str:
    p = data.person
    c = data.contact
    t = data.trip
    a = data.accommodation

    return "\n".join(
        [
            "Паспорт:",
            f"- ФИО: {p.full_name or '-'}",
            f"- Номер: {p.passport_number or '-'}",
            f"- Дата рождения: {_d(p.date_of_birth)}",
            f"- Пол (MDAC): {p.sex or '-'}",
            f"- Гражданство (ISO3): {p.nationality_code or '-'}",
            f"- Место рождения (ISO3): {p.place_of_birth_code or '-'}",
            f"- Срок действия: {_d(p.passport_expiry)}",
            "",
            "Контакты:",
            f"- Email: {c.email or '-'}",
            f"- Телефон код: {c.phone_country_code or '-'}",
            f"- Телефон номер: {c.phone_number or '-'}",
            "",
            "Поездка:",
            f"- Прибытие: {_d(t.arrival_date)}",
            f"- Выезд: {_d(t.departure_date)}",
            f"- Способ (MDAC): {t.travel_mode or '-'}",
            f"- Рейс/судно: {t.vessel_name or '-'}",
            f"- Страна отправления (ISO3): {t.embark_country_code or '-'}",
            "",
            "Проживание:",
            f"- Тип (MDAC): {a.stay_type or '-'}",
            f"- Адрес 1: {a.address1 or '-'}",
            f"- Адрес 2: {a.address2 or '-'}",
            f"- Штат (MDAC): {a.state_code or '-'}",
            f"- Индекс: {a.postcode or '-'}",
            f"- Город (текст): {a.city_text or '-'}",
        ]
    )

