from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from services.admin_client import AdminClient
from services.history_service import HistoryService

history_service = HistoryService()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )


async def send_command(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    admin_client = AdminClient()

    try:
        response = await admin_client.submit_command(
            service=data["service"],
            command_type=data["command_type"],
            data=data["data"],
        )

        request_id = response.get("request_id")

        await history_service.create_command(
            user_id=user_id,
            request_id=request_id,
            service=data["service"],
            command_type=data["command_type"],
            payload=data["data"],
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Проверить статус",
                        callback_data=f"status:check:{request_id}",
                    ),
                ],
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )

        await message.answer(
            f"✅ Команда отправлена!\n\n"
            f"📋 Request ID: `{request_id}`\n"
            f"📊 Статус: {response.get('status')}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке команды: {e}")
    finally:
        await admin_client.close()


async def send_command_with_file(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    admin_client = AdminClient()

    try:
        file_payload = data.get("file")
        response = await admin_client.submit_command(
            service=data["service"],
            command_type=data["command_type"],
            data=data["data"],
            file_payload=file_payload,
        )

        request_id = response.get("request_id")

        await history_service.create_command(
            user_id=user_id,
            request_id=request_id,
            service=data["service"],
            command_type=data["command_type"],
            payload={**data["data"], "has_file": True},
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Проверить статус",
                        callback_data=f"status:check:{request_id}",
                    ),
                ],
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        )

        await message.answer(
            f"✅ Команда с файлом отправлена!\n\n"
            f"📋 Request ID: `{request_id}`\n"
            f"📊 Статус: {response.get('status')}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке команды: {e}")
    finally:
        await admin_client.close()

