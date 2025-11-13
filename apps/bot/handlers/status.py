import json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.admin_client import AdminClient
from services.history_service import HistoryService

router = Router()
history_service = HistoryService()


class StatusStates(StatesGroup):
    waiting_request_id = State()


@router.callback_query(F.data == "status:check")
async def callback_check_status(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📊 Проверка статуса\n\nОтправьте Request ID:",
    )
    await state.set_state(StatusStates.waiting_request_id)
    await callback.answer()


@router.callback_query(F.data.startswith("status:check:"))
async def callback_check_status_direct(callback: CallbackQuery):
    request_id = callback.data.split(":")[2]
    await show_status_for_callback(callback, request_id)
    await callback.answer()


async def show_status(message: Message, request_id: str):
    admin_client = AdminClient()

    try:
        status_data = await admin_client.get_message_status(request_id)

        status = status_data.get("status", "unknown")
        response = status_data.get("response")
        error = status_data.get("error")
        await history_service.update_command_status(request_id, status, response, error)

        service = status_data.get("service", "unknown")
        created_at = status_data.get("created_at", "")
        updated_at = status_data.get("updated_at", "")

        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "error": "❌",
        }.get(status, "❓")

        text = (
            f"{status_emoji} Статус запроса\n\n"
            f"📋 Request ID: `{request_id}`\n"
            f"🔧 Сервис: {service}\n"
            f"📊 Статус: {status}\n"
            f"🕐 Создан: {created_at}\n"
            f"🕑 Обновлен: {updated_at}\n"
        )

        if error:
            text += f"\n❌ Ошибка: {error}"
        elif response:
            text += f"\n📄 Ответ:\n```json\n{json.dumps(response, indent=2, ensure_ascii=False)}\n```"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить", callback_data=f"status:refresh:{request_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📜 В историю", callback_data="history:list"
                    ),
                ],
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )

        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        error_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )
        await message.answer(
            f"❌ Ошибка при получении статуса: {e}",
            reply_markup=error_keyboard,
        )
    finally:
        await admin_client.close()


async def show_status_for_callback(callback: CallbackQuery, request_id: str):
    admin_client = AdminClient()

    try:
        status_data = await admin_client.get_message_status(request_id)

        status = status_data.get("status", "unknown")
        response = status_data.get("response")
        error = status_data.get("error")
        await history_service.update_command_status(request_id, status, response, error)

        service = status_data.get("service", "unknown")
        created_at = status_data.get("created_at", "")
        updated_at = status_data.get("updated_at", "")

        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "error": "❌",
        }.get(status, "❓")

        text = (
            f"{status_emoji} Статус запроса\n\n"
            f"📋 Request ID: `{request_id}`\n"
            f"🔧 Сервис: {service}\n"
            f"📊 Статус: {status}\n"
            f"🕐 Создан: {created_at}\n"
            f"🕑 Обновлен: {updated_at}\n"
        )

        if error:
            text += f"\n❌ Ошибка: {error}"
        elif response:
            text += f"\n📄 Ответ:\n```json\n{json.dumps(response, indent=2, ensure_ascii=False)}\n```"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить", callback_data=f"status:refresh:{request_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📜 В историю", callback_data="history:list"
                    ),
                ],
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )

        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        error_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )
        await callback.message.edit_text(
            f"❌ Ошибка при получении статуса: {e}",
            reply_markup=error_keyboard,
        )
    finally:
        await admin_client.close()


@router.message(StatusStates.waiting_request_id)
async def process_status_check(message: Message, state: FSMContext):
    request_id = message.text.strip()
    await show_status(message, request_id)
    await state.clear()


@router.callback_query(F.data.startswith("status:refresh:"))
async def callback_refresh_status(callback: CallbackQuery):
    request_id = callback.data.split(":")[2]

    admin_client = AdminClient()

    try:
        status_data = await admin_client.get_message_status(request_id)

        status = status_data.get("status", "unknown")
        response = status_data.get("response")
        error = status_data.get("error")
        await history_service.update_command_status(request_id, status, response, error)

        updated_at = status_data.get("updated_at", "")

        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "error": "❌",
        }.get(status, "❓")

        text = (
            f"{status_emoji} Статус: {status}\n"
            f"🕑 Обновлен: {updated_at}\n"
        )

        if error:
            text += f"\n❌ Ошибка: {error}"
        elif response:
            text += f"\n📄 Ответ:\n```json\n{json.dumps(response, indent=2, ensure_ascii=False)}\n```"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить", callback_data=f"status:refresh:{request_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📜 В историю", callback_data="history:list"
                    ),
                ],
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )

        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer("✅ Обновлено")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
    finally:
        await admin_client.close()


@router.message(Command("status"))
async def cmd_status(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /status <request_id>")
        return

    request_id = parts[1]
    await show_status(message, request_id)
