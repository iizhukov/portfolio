import json
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.history_service import HistoryService
from services.admin_client import AdminClient

router = Router()
history_service = HistoryService()


def format_command_history_item(history_item, index: int) -> str:
    status_emoji = {
        "pending": "⏳",
        "completed": "✅",
        "error": "❌",
    }.get(history_item.status, "❓")

    created = history_item.created_at
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except:
            pass

    time_str = created.strftime("%H:%M:%S") if isinstance(created, datetime) else str(created)

    text = (
        f"{index}. {status_emoji} {history_item.command_type}\n"
        f"   📋 {history_item.request_id[:8]}...\n"
        f"   🕐 {time_str}"
    )
    return text


@router.callback_query(F.data == "history:list")
async def callback_history_list(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        history_items = await history_service.get_user_history(user_id, limit=10)

        if not history_items:
            await callback.message.edit_text(
                "📜 История команд\n\nИстория пуста.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
                    ]
                ),
            )
            await callback.answer()
            return

        text = "📜 История команд\n\n"
        buttons = []

        for idx, item in enumerate(history_items, 1):
            text += format_command_history_item(item, idx) + "\n\n"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{idx}. {item.command_type} ({item.status})",
                        callback_data=f"history:detail:{item.request_id}",
                    )
                ]
            )

        buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")])

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        await callback.answer()
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при получении истории: {e}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
                ]
            ),
        )
        await callback.answer()


@router.callback_query(F.data.startswith("history:detail:"))
async def callback_history_detail(callback: CallbackQuery):
    request_id = callback.data.split(":")[2]

    try:
        history_item = await history_service.get_command_by_request_id(request_id)

        if not history_item:
            await callback.answer("Команда не найдена", show_alert=True)
            return

        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "error": "❌",
        }.get(history_item.status, "❓")

        text = (
            f"{status_emoji} Детали команды\n\n"
            f"📋 Request ID: `{history_item.request_id}`\n"
            f"🔧 Сервис: {history_item.service}\n"
            f"📝 Команда: {history_item.command_type}\n"
            f"📊 Статус: {history_item.status}\n"
            f"🕐 Создана: {history_item.created_at}\n"
            f"🕑 Обновлена: {history_item.updated_at}\n"
        )

        if history_item.payload:
            text += f"\n📄 Payload:\n```json\n{json.dumps(history_item.payload, indent=2, ensure_ascii=False)}\n```"

        if history_item.error:
            text += f"\n❌ Ошибка: {history_item.error}"

        if history_item.response:
            text += f"\n📤 Ответ:\n```json\n{json.dumps(history_item.response, indent=2, ensure_ascii=False)}\n```"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить статус",
                        callback_data=f"status:refresh:{request_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Полный статус",
                        callback_data=f"status:check:{request_id}",
                    ),
                ],
                [InlineKeyboardButton(text="🔙 История", callback_data="history:list")],
            ]
        )

        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
