from __future__ import annotations

import asyncio
from dataclasses import dataclass

from playwright.async_api import async_playwright

from mdac_bot.models import UnifiedData
from mdac_bot.sites.utils import format_ddmmyyyy


MDAC_URL = "https://imigresen-online.imi.gov.my/mdac/main?registerMain"


@dataclass(frozen=True)
class MdacRunResult:
    screenshot_png: bytes


def mdac_required_fields(data: UnifiedData) -> list[str]:
    missing: list[str] = []

    if not data.person.full_name:
        missing.append("person.full_name")
    if not data.person.passport_number:
        missing.append("person.passport_number")
    if not data.person.date_of_birth:
        missing.append("person.date_of_birth")
    if not data.person.nationality_code:
        missing.append("person.nationality_code")
    if not data.person.place_of_birth_code:
        missing.append("person.place_of_birth_code")
    if not data.person.sex:
        missing.append("person.sex")
    if not data.person.passport_expiry:
        missing.append("person.passport_expiry")

    if not data.contact.email:
        missing.append("contact.email")
    if not data.contact.phone_country_code:
        missing.append("contact.phone_country_code")
    if not data.contact.phone_number:
        missing.append("contact.phone_number")

    if not data.trip.arrival_date:
        missing.append("trip.arrival_date")
    if not data.trip.departure_date:
        missing.append("trip.departure_date")
    if not data.trip.vessel_name:
        missing.append("trip.vessel_name")
    if not data.trip.travel_mode:
        missing.append("trip.travel_mode")
    if not data.trip.embark_country_code:
        missing.append("trip.embark_country_code")

    if not data.accommodation.stay_type:
        missing.append("accommodation.stay_type")
    if not data.accommodation.address1:
        missing.append("accommodation.address1")
    if not data.accommodation.state_code:
        missing.append("accommodation.state_code")
    if not data.accommodation.postcode:
        missing.append("accommodation.postcode")
    if not data.accommodation.city_text:
        missing.append("accommodation.city_text")

    return missing


async def _maybe_select(page, selector: str, value: str | None) -> None:
    if value is None or value == "":
        return
    await page.locator(selector).select_option(value=value)


async def _maybe_fill(page, selector: str, value: str | None) -> None:
    if value is None or value == "":
        return
    await page.locator(selector).fill(value)


async def _select_city(page, *, city_text: str | None) -> None:
    if not city_text:
        return
    city = page.locator("#accommodationCity")
    for _ in range(20):
        count = await city.locator("option").count()
        if count > 1:
            break
        await asyncio.sleep(0.25)

    options = await city.locator("option").all()
    target = None
    for opt in options:
        t = (await opt.text_content()) or ""
        if city_text.upper() in t.upper():
            target = await opt.get_attribute("value")
            break

    if target:
        await city.select_option(value=target)


async def _select_state_and_city(page, *, state_code: str | None, city_text: str | None) -> None:
    if not state_code:
        return
    await _maybe_select(page, "#accommodationState", state_code)
    await _select_city(page, city_text=city_text)


async def mdac_fill_preview(data: UnifiedData, *, headless: bool) -> MdacRunResult:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(MDAC_URL, wait_until="domcontentloaded")

        await _maybe_fill(page, "#name", data.person.full_name)
        await _maybe_fill(page, "#passNo", data.person.passport_number)
        await _maybe_fill(page, "#dob", format_ddmmyyyy(data.person.date_of_birth))
        await _maybe_select(page, "#nationality", data.person.nationality_code)
        await _maybe_select(page, "#pob", data.person.place_of_birth_code)
        await _maybe_select(page, "#sex", data.person.sex)
        await _maybe_fill(page, "#passExpDte", format_ddmmyyyy(data.person.passport_expiry))
        await _maybe_fill(page, "#email", data.contact.email)
        await _maybe_fill(page, "#confirmEmail", data.contact.email)

        await _maybe_select(page, "#region", data.contact.phone_country_code)
        await _maybe_fill(page, "#mobile", data.contact.phone_number)

        await _maybe_fill(page, "#arrDt", format_ddmmyyyy(data.trip.arrival_date))
        await _maybe_fill(page, "#depDt", format_ddmmyyyy(data.trip.departure_date))
        await _maybe_fill(page, "#vesselNm", data.trip.vessel_name)
        await _maybe_select(page, "#trvlMode", data.trip.travel_mode)
        await _maybe_select(page, "#embark", data.trip.embark_country_code)

        await _maybe_select(page, "#accommodationStay", data.accommodation.stay_type)
        await _maybe_fill(page, "#accommodationAddress1", data.accommodation.address1)
        await _maybe_fill(page, "#accommodationAddress2", data.accommodation.address2)
        await _maybe_fill(page, "#accommodationPostcode", data.accommodation.postcode)
        await _select_state_and_city(page, state_code=data.accommodation.state_code, city_text=data.accommodation.city_text)

        png = await page.screenshot(full_page=True)
        await context.close()
        await browser.close()

        return MdacRunResult(screenshot_png=png)


async def mdac_submit(data: UnifiedData, *, headless: bool) -> MdacRunResult:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(MDAC_URL, wait_until="domcontentloaded")

        await _maybe_fill(page, "#name", data.person.full_name)
        await _maybe_fill(page, "#passNo", data.person.passport_number)
        await _maybe_fill(page, "#dob", format_ddmmyyyy(data.person.date_of_birth))
        await _maybe_select(page, "#nationality", data.person.nationality_code)
        await _maybe_select(page, "#pob", data.person.place_of_birth_code)
        await _maybe_select(page, "#sex", data.person.sex)
        await _maybe_fill(page, "#passExpDte", format_ddmmyyyy(data.person.passport_expiry))
        await _maybe_fill(page, "#email", data.contact.email)
        await _maybe_fill(page, "#confirmEmail", data.contact.email)

        await _maybe_select(page, "#region", data.contact.phone_country_code)
        await _maybe_fill(page, "#mobile", data.contact.phone_number)

        await _maybe_fill(page, "#arrDt", format_ddmmyyyy(data.trip.arrival_date))
        await _maybe_fill(page, "#depDt", format_ddmmyyyy(data.trip.departure_date))
        await _maybe_fill(page, "#vesselNm", data.trip.vessel_name)
        await _maybe_select(page, "#trvlMode", data.trip.travel_mode)
        await _maybe_select(page, "#embark", data.trip.embark_country_code)

        await _maybe_select(page, "#accommodationStay", data.accommodation.stay_type)
        await _maybe_fill(page, "#accommodationAddress1", data.accommodation.address1)
        await _maybe_fill(page, "#accommodationAddress2", data.accommodation.address2)
        await _maybe_fill(page, "#accommodationPostcode", data.accommodation.postcode)
        await _select_state_and_city(page, state_code=data.accommodation.state_code, city_text=data.accommodation.city_text)

        await page.locator("#submit").click()
        await page.wait_for_load_state("domcontentloaded")

        png = await page.screenshot(full_page=True)
        await context.close()
        await browser.close()

        return MdacRunResult(screenshot_png=png)
