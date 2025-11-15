import base64

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.commands.base import send_command, send_command_with_file, get_cancel_keyboard

router = Router()


def ensure_data_dict(state_data: dict) -> dict:
    if "data" not in state_data:
        state_data["data"] = {}
    return state_data["data"]


class ConnectionsStates(StatesGroup):
    # create_connection
    waiting_label = State()
    waiting_type = State()
    waiting_href = State()
    waiting_value = State()
    # update_connection
    waiting_connection_id = State()
    waiting_update_field = State()
    # delete_connection
    waiting_delete_id = State()
    # update_status
    waiting_status_value = State()
    # update_working
    waiting_working_on = State()
    waiting_percentage = State()
    # update_image
    waiting_image_file = State()
    waiting_image_name = State()
    waiting_image_path = State()


def get_commands_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать", callback_data="cmd:connections:create_connection"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Обновить", callback_data="cmd:connections:update_connection"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить", callback_data="cmd:connections:delete_connection"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статус", callback_data="cmd:connections:update_status"
                ),
                InlineKeyboardButton(
                    text="💼 Working", callback_data="cmd:connections:update_working"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🖼️ Изображение", callback_data="cmd:connections:update_image"
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="cmd:send")],
        ]
    )


# Create Connection
@router.callback_query(F.data == "cmd:connections:create_connection")
async def callback_create_connection(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        command_type="create_connection",
        data={},
        step=1,
        total_steps=4,
        bot_message_id=callback.message.message_id,
    )
    await callback.message.edit_text(
        "➕ Создание соединения\n\n"
        "Шаг 1/4: Введите название (label):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_label)
    await callback.answer()


@router.message(ConnectionsStates.waiting_label)
async def process_label(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("❌ Название не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        await message.edit_text(f"✅ Label: {message.text.strip()}")
    except Exception:
        await message.delete()
    
    data = await state.get_data()
    ensure_data_dict(data)["label"] = message.text.strip()
    await state.update_data(data=data, step=2)
    
    from handlers.commands.base import edit_or_send_message
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        "➕ Создание соединения\n\n"
        f"✅ Label: {message.text.strip()}\n\n"
        "Шаг 2/4: Введите тип соединения (social/email):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_type)


@router.message(ConnectionsStates.waiting_type)
async def process_type(message: Message, state: FSMContext):
    if message.text not in ["social", "email"]:
        await message.answer("❌ Тип должен быть 'social' или 'email'. Попробуйте еще раз:")
        return

    try:
        await message.edit_text(f"✅ Type: {message.text}")
    except Exception:
        await message.delete()

    data = await state.get_data()
    ensure_data_dict(data)["type"] = message.text
    await state.update_data(data=data, step=3)
    
    from handlers.commands.base import edit_or_send_message
    cmd_data = data.get("data", {})
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        "➕ Создание соединения\n\n"
        f"✅ Label: {cmd_data.get('label')}\n"
        f"✅ Type: {message.text}\n\n"
        "Шаг 3/4: Введите ссылку (href):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_href)


@router.message(ConnectionsStates.waiting_href)
async def process_href(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("❌ Ссылка не может быть пустой. Попробуйте еще раз:")
        return
    
    try:
        await message.edit_text(f"✅ Href: {message.text.strip()}")
    except Exception:
        await message.delete()
    
    data = await state.get_data()
    ensure_data_dict(data)["href"] = message.text.strip()
    await state.update_data(data=data, step=4)
    
    from handlers.commands.base import edit_or_send_message
    cmd_data = data.get("data", {})
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        "➕ Создание соединения\n\n"
        f"✅ Label: {cmd_data.get('label')}\n"
        f"✅ Type: {cmd_data.get('type')}\n"
        f"✅ Href: {message.text.strip()}\n\n"
        "Шаг 4/4: Введите значение (value):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_value)


@router.message(ConnectionsStates.waiting_value)
async def process_value(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("❌ Значение не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        await message.edit_text(f"✅ Value: {message.text.strip()}")
    except Exception:
        await message.delete()
    
    data = await state.get_data()
    ensure_data_dict(data)["value"] = message.text.strip()
    await state.update_data(data=data)
    
    from handlers.commands.base import edit_or_send_message
    cmd_data = data.get("data", {})
    preview_text = (
        "📋 Предпросмотр данных:\n\n"
        f"📝 Label: {cmd_data.get('label')}\n"
        f"🏷️ Type: {cmd_data.get('type')}\n"
        f"🔗 Href: {cmd_data.get('href')}\n"
        f"📌 Value: {cmd_data.get('value')}\n\n"
        "⏳ Отправляю команду..."
    )
    
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        preview_text,
        reply_markup=None,
    )
    await send_command(message, state)


# Update Connection
@router.callback_query(F.data == "cmd:connections:update_connection")
async def callback_update_connection(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="update_connection", data={})
    await callback.message.edit_text(
        "✏️ Обновление соединения\n\nВведите ID соединения:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_connection_id)
    await callback.answer()


@router.message(ConnectionsStates.waiting_connection_id)
async def process_connection_id(message: Message, state: FSMContext):
    try:
        connection_id = int(message.text)
        data = await state.get_data()
        ensure_data_dict(data)["id"] = connection_id
        await state.update_data(data=data)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📝 Label", callback_data="update_field:label"
                    ),
                    InlineKeyboardButton(text="🔗 Href", callback_data="update_field:href"),
                ],
                [
                    InlineKeyboardButton(
                        text="📌 Value", callback_data="update_field:value"
                    ),
                    InlineKeyboardButton(text="🏷️ Type", callback_data="update_field:type"),
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Готово", callback_data="update_field:done"
                    ),
                ],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
            ]
        )

        await message.answer(
            "Выберите поле для обновления или нажмите 'Готово' для отправки:",
            reply_markup=keyboard,
        )
        await state.set_state(ConnectionsStates.waiting_update_field)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте еще раз:")


@router.callback_query(F.data.startswith("update_field:"))
async def callback_update_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]

    if field == "done":
        data = await state.get_data()
        cmd_data = ensure_data_dict(data)
        if not cmd_data or len(cmd_data) <= 1:  # Только id
            await callback.answer("Выберите хотя бы одно поле для обновления", show_alert=True)
            return
        await callback.message.edit_text("⏳ Отправляю команду...")
        await send_command(callback.message, state)
        await callback.answer()
        return

    field_prompts = {
        "label": "Введите новое название (label):",
        "href": "Введите новую ссылку (href):",
        "value": "Введите новое значение (value):",
        "type": "Введите новый тип (social/email):",
    }

    await callback.message.edit_text(
        field_prompts.get(field, "Введите значение:"), reply_markup=get_cancel_keyboard()
    )
    await state.update_data(current_field=field)
    await state.set_state(ConnectionsStates.waiting_update_field)
    await callback.answer()


@router.message(ConnectionsStates.waiting_update_field)
async def process_update_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    current_field = data.get("current_field")

    if current_field == "type" and message.text not in ["social", "email"]:
        await message.answer("❌ Тип должен быть 'social' или 'email'. Попробуйте еще раз:")
        return

    ensure_data_dict(data)[current_field] = message.text
    data.pop("current_field", None)
    await state.update_data(data=data)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Label", callback_data="update_field:label"
                ),
                InlineKeyboardButton(text="🔗 Href", callback_data="update_field:href"),
            ],
            [
                InlineKeyboardButton(
                    text="📌 Value", callback_data="update_field:value"
                ),
                InlineKeyboardButton(text="🏷️ Type", callback_data="update_field:type"),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Готово", callback_data="update_field:done"
                ),
            ],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )

    await message.answer(
        f"✅ Поле '{current_field}' обновлено.\n\nВыберите еще одно поле или нажмите 'Готово':",
        reply_markup=keyboard,
    )


# Delete Connection
@router.callback_query(F.data == "cmd:connections:delete_connection")
async def callback_delete_connection(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="delete_connection", data={})
    await callback.message.edit_text(
        "🗑️ Удаление соединения\n\nВведите ID соединения:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_delete_id)
    await callback.answer()


@router.message(ConnectionsStates.waiting_delete_id)
async def process_delete_id(message: Message, state: FSMContext):
    try:
        connection_id = int(message.text)
        data = await state.get_data()
        ensure_data_dict(data)["id"] = connection_id
        await state.update_data(data=data)
        await send_command(message, state)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте еще раз:")


# Update Status
@router.callback_query(F.data == "cmd:connections:update_status")
async def callback_update_status(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="update_status", data={})
    await callback.message.edit_text(
        "📊 Обновление статуса\n\nВведите статус (например: active, inactive):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_status_value)
    await callback.answer()


@router.message(ConnectionsStates.waiting_status_value)
async def process_status_value(message: Message, state: FSMContext):
    data = await state.get_data()
    ensure_data_dict(data)["status"] = message.text
    await state.update_data(data=data)
    await send_command(message, state)


# Update Working
@router.callback_query(F.data == "cmd:connections:update_working")
async def callback_update_working(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="update_working", data={})
    await callback.message.edit_text(
        "💼 Обновление Working\n\nВведите над чем работаете:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_working_on)
    await callback.answer()


@router.message(ConnectionsStates.waiting_working_on)
async def process_working_on(message: Message, state: FSMContext):
    data = await state.get_data()
    ensure_data_dict(data)["working_on"] = message.text
    await state.update_data(data=data)
    await message.answer("Введите процент выполнения (0-100):", reply_markup=get_cancel_keyboard())
    await state.set_state(ConnectionsStates.waiting_percentage)


@router.message(ConnectionsStates.waiting_percentage)
async def process_percentage(message: Message, state: FSMContext):
    try:
        percentage = int(message.text)
        if not 0 <= percentage <= 100:
            await message.answer("❌ Процент должен быть от 0 до 100. Попробуйте еще раз:")
            return
        data = await state.get_data()
        ensure_data_dict(data)["percentage"] = percentage
        await state.update_data(data=data)
        await send_command(message, state)
    except ValueError:
        await message.answer("❌ Процент должен быть числом. Попробуйте еще раз:")


# Update Image
@router.callback_query(F.data == "cmd:connections:update_image")
async def callback_update_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="update_image", data={})
    await callback.message.edit_text(
        "🖼️ Обновление изображения\n\nОтправьте изображение (фото):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_image_file)
    await callback.answer()


@router.message(ConnectionsStates.waiting_image_file)
async def process_image_file(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте изображение (фото).")
        return

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file.file_path)

    image_bytes = file_bytes.read()
    base64_content = base64.b64encode(image_bytes).decode("utf-8")

    extension = "jpg"
    if file.file_path:
        ext = file.file_path.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            extension = ext

    data = await state.get_data()
    data["file"] = {
        "name": "image",
        "extension": extension,
        "path": "",
        "content": base64_content,
    }
    data["data"] = {
        "filename": f"image.{extension}",
        "content_type": f"image/{extension}",
        "url": "",
    }
    await state.update_data(data=data)

    await message.answer(
        "✅ Изображение получено!\n\nВведите имя файла (без расширения) или нажмите /skip для пропуска:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_image_name)


@router.message(ConnectionsStates.waiting_image_name)
async def process_image_name(message: Message, state: FSMContext):
    if message.text == "/skip":
        name = "image"
    else:
        name = message.text.strip()

    data = await state.get_data()
    file_info = data.get("file", {})
    extension = file_info.get("extension", "jpg")
    file_info["name"] = name
    data["file"] = file_info
    ensure_data_dict(data)["filename"] = f"{name}.{extension}"
    await state.update_data(data=data)

    await message.answer(
        "Введите путь для сохранения (или /skip для пропуска):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ConnectionsStates.waiting_image_path)


@router.message(ConnectionsStates.waiting_image_path)
async def process_image_path(message: Message, state: FSMContext):
    path = message.text.strip() if message.text != "/skip" else ""

    data = await state.get_data()
    file_info = data.get("file", {})
    file_info["path"] = path
    data["file"] = file_info
    await state.update_data(data=data)

    await send_command_with_file(message, state)

