from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.commands.connections import router as connections_router
from handlers.commands.projects import router as projects_router

router = Router()


class CommandStates(StatesGroup):
    waiting_service = State()
    waiting_command_type = State()


def get_services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Connections", callback_data="service:connections")],
            [InlineKeyboardButton(text="📁 Projects", callback_data="service:projects")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")],
        ]
    )


@router.callback_query(F.data == "cmd:send")
async def callback_send_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔧 Отправка команды\n\nВыберите сервис:",
        reply_markup=get_services_keyboard(),
    )
    await state.set_state(CommandStates.waiting_service)
    await callback.answer()


@router.callback_query(F.data == "cmd:cancel")
async def callback_cancel_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Команда отменена.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Меню", callback_data="menu:main")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("service:"))
async def callback_select_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split(":")[1]
    await state.update_data(service=service)

    if service == "connections":
        from handlers.commands.connections import get_commands_keyboard
        await callback.message.edit_text(
            f"🔗 {service.capitalize()} Service\n\nВыберите команду:",
            reply_markup=get_commands_keyboard(),
        )
        await state.set_state(CommandStates.waiting_command_type)
    elif service == "projects":
        from handlers.commands.projects import get_commands_keyboard
        await callback.message.edit_text(
            f"📁 {service.capitalize()} Service\n\nВыберите команду:",
            reply_markup=get_commands_keyboard(),
        )
        await state.set_state(CommandStates.waiting_command_type)
    else:
        await callback.answer("Сервис не поддерживается", show_alert=True)

    await callback.answer()


router.include_router(connections_router)
router.include_router(projects_router)

__all__ = ["router", "CommandStates", "get_services_keyboard"]

