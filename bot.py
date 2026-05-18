from __future__ import annotations

import asyncio
import io

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

from mdac_bot.classify import classify_document
from mdac_bot.config import load_config
from mdac_bot.extractors.flight_ticket import extract_ticket
from mdac_bot.extractors.hotel_booking import extract_hotel_booking
from mdac_bot.extractors.passport import extract_passport
from mdac_bot.formatting import format_profile
from mdac_bot.merge import merge_data
from mdac_bot.ocr import run_tesseract
from mdac_bot.setters import set_field
from mdac_bot.sites.mdac import mdac_fill_preview, mdac_required_fields, mdac_submit
from mdac_bot.storage import UserState, UserStore


def _keyboard_preview() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отправить (Submit)", callback_data="mdac_submit"),
                InlineKeyboardButton(text="Отменить", callback_data="mdac_cancel"),
            ]
        ]
    )


async def cmd_start(message: Message) -> None:
    await message.answer(
        "\n".join(
            [
                "Отправьте фото паспорта/билета/брони отеля.",
                "Подпись к фото (опционально): passport | ticket | hotel",
                "",
                "Команды:",
                "- /profile",
                "- /set <путь> <значение>  (пример: /set contact.email test@example.com)",
                "- /fill_mdac",
                "- /reset",
            ]
        )
    )


def _doc_type_from_caption(caption: str | None) -> str | None:
    if not caption:
        return None
    c = caption.strip().lower()
    if c in {"passport", "паспорт"}:
        return "passport"
    if c in {"ticket", "билет"}:
        return "ticket"
    if c in {"hotel", "отель", "бронь"}:
        return "hotel"
    return None


async def cmd_reset(message: Message, store: UserStore) -> None:
    store.reset(message.from_user.id)
    await message.answer("Очищено.")


async def cmd_profile(message: Message, store: UserStore) -> None:
    state = store.load(message.from_user.id)
    missing = mdac_required_fields(state.data)
    text = format_profile(state.data)
    if missing:
        text += "\n\nНе хватает для MDAC:\n" + "\n".join([f"- {m}" for m in missing])
    await message.answer(text)


async def cmd_set(message: Message, store: UserStore) -> None:
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /set person.full_name IVAN IVANOV")
        return

    path = parts[1]
    value = parts[2]

    state = store.load(message.from_user.id)
    try:
        set_field(state.data, path, value)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        return

    store.save(message.from_user.id, state)
    await message.answer("Сохранено.")


async def _download_photo(bot: Bot, message: Message) -> bytes:
    photo = message.photo[-1]
    f = await bot.get_file(photo.file_id)
    buf = io.BytesIO()
    await bot.download_file(f.file_path, destination=buf)
    return buf.getvalue()


async def on_photo(message: Message, bot: Bot, store: UserStore, tesseract_cmd: str | None) -> None:
    img = await _download_photo(bot, message)
    ocr = run_tesseract(img, tesseract_cmd=tesseract_cmd)
    doc_type = _doc_type_from_caption(message.caption) or classify_document(ocr.text)

    state = store.load(message.from_user.id)
    state.ocr_texts[doc_type] = ocr.text

    incoming = None
    if doc_type == "passport":
        incoming = extract_passport(ocr.text).data
    elif doc_type == "ticket":
        incoming = extract_ticket(ocr.text).data
    elif doc_type == "hotel":
        incoming = extract_hotel_booking(ocr.text).data

    if incoming:
        state.data = merge_data(state.data, incoming)
        store.save(message.from_user.id, state)
        await message.answer(f"Распознано: {doc_type}. Обновил профиль. /profile")
    else:
        store.save(message.from_user.id, state)
        await message.answer(f"Распознано: {doc_type}. Поля не извлеклись, но OCR-текст сохранён. /profile")


async def cmd_fill_mdac(message: Message, store: UserStore, headless: bool) -> None:
    state = store.load(message.from_user.id)
    missing = mdac_required_fields(state.data)
    if missing:
        await message.answer("Сначала заполните недостающие поля через /set:\n" + "\n".join([f"- {m}" for m in missing]))
        return

    await message.answer("Заполняю MDAC и присылаю превью…")
    res = await mdac_fill_preview(state.data, headless=headless)
    await message.answer_photo(
        photo=res.screenshot_png,
        caption="Проверьте данные. Если всё ок — подтвердите отправку.",
        reply_markup=_keyboard_preview(),
    )


async def on_callback(callback: CallbackQuery, store: UserStore, headless: bool) -> None:
    if callback.data == "mdac_cancel":
        await callback.message.answer("Ок, отменено.")
        await callback.answer()
        return

    if callback.data != "mdac_submit":
        await callback.answer()
        return

    state = store.load(callback.from_user.id)
    missing = mdac_required_fields(state.data)
    if missing:
        await callback.message.answer("Не хватает полей:\n" + "\n".join([f"- {m}" for m in missing]))
        await callback.answer()
        return

    await callback.message.answer("Отправляю форму…")
    res = await mdac_submit(state.data, headless=headless)
    await callback.message.answer_photo(photo=res.screenshot_png, caption="Результат отправки.")
    await callback.answer()


async def main() -> None:
    load_dotenv()
    cfg = load_config()

    store = UserStore(cfg.data_dir)
    bot = Bot(token=cfg.telegram_bot_token)
    dp = Dispatcher()

    async def _reset(m: Message) -> None:
        await cmd_reset(m, store)

    async def _profile(m: Message) -> None:
        await cmd_profile(m, store)

    async def _set(m: Message) -> None:
        await cmd_set(m, store)

    async def _fill_mdac(m: Message) -> None:
        await cmd_fill_mdac(m, store, cfg.headless)

    async def _photo(m: Message) -> None:
        await on_photo(m, bot, store, cfg.tesseract_cmd)

    async def _cb(c: CallbackQuery) -> None:
        await on_callback(c, store, cfg.headless)

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(_reset, Command("reset"))
    dp.message.register(_profile, Command("profile"))
    dp.message.register(_set, Command("set"))
    dp.message.register(_fill_mdac, Command("fill_mdac"))

    dp.message.register(_photo, F.photo)
    dp.callback_query.register(_cb)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
