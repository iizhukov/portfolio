from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from core.config import settings

router = Router()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔧 Отправить команду", callback_data="cmd:send"),
            ],
            [
                InlineKeyboardButton(text="📊 Статус запроса", callback_data="status:check"),
                InlineKeyboardButton(text="📜 История", callback_data="history:list"),
            ],
        ]
    )


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id

    if settings.ALLOWED_USER_IDS and user_id not in settings.ALLOWED_USER_IDS:
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    await message.answer(
        "👋 Привет! Я бот для управления Admin Service.\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("📋 Главное меню:", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "menu:main")
async def callback_menu_main(callback):
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()

