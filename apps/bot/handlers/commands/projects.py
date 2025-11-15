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


class ProjectsStates(StatesGroup):
    # create_project
    waiting_name = State()
    waiting_type = State()
    waiting_file_type = State()
    waiting_parent_id = State()
    waiting_url = State()
    waiting_file = State()
    waiting_file_name = State()
    waiting_file_path = State()
    # update_project
    waiting_project_id = State()
    waiting_update_field = State()
    # delete_project
    waiting_delete_id = State()


VALID_FILE_TYPES = [
    "folder", "folder-filled", "readme", "architecture", 
    "demo", "github", "database", "swagger"
]


def get_commands_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать", callback_data="cmd:projects:create_project"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Обновить", callback_data="cmd:projects:update_project"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить", callback_data="cmd:projects:delete_project"
                ),
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="cmd:send")],
        ]
    )


def get_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📁 Папка", callback_data="type:folder"),
                InlineKeyboardButton(text="📄 Файл", callback_data="type:file"),
            ],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )


def get_file_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 README", callback_data="file_type:readme"),
                InlineKeyboardButton(text="📊 Architecture", callback_data="file_type:architecture"),
            ],
            [
                InlineKeyboardButton(text="🌐 Demo", callback_data="file_type:demo"),
                InlineKeyboardButton(text="💻 GitHub", callback_data="file_type:github"),
            ],
            [
                InlineKeyboardButton(text="🗄️ Database", callback_data="file_type:database"),
                InlineKeyboardButton(text="📋 Swagger", callback_data="file_type:swagger"),
            ],
            [
                InlineKeyboardButton(text="⏭️ Пропустить", callback_data="file_type:skip"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel"),
            ],
        ]
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="cmd:projects:create_project")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )


# Create Project
@router.callback_query(F.data == "cmd:projects:create_project")
async def callback_create_project(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        command_type="create_project",
        data={},
        step=1,
        total_steps=5,
        bot_message_id=callback.message.message_id,
    )
    await callback.message.edit_text(
        "➕ Создание проекта\n\n"
        "Шаг 1/5: Введите название проекта:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_name)
    await callback.answer()


@router.message(ProjectsStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("❌ Название не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        await message.edit_text(f"✅ Name: {message.text.strip()}")
    except Exception:
        await message.delete()
    
    data = await state.get_data()
    ensure_data_dict(data)["name"] = message.text.strip()
    await state.update_data(data=data, step=2)
    
    from handlers.commands.base import edit_or_send_message
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        "➕ Создание проекта\n\n"
        f"✅ Name: {message.text.strip()}\n\n"
        "Шаг 2/5: Выберите тип проекта:",
        reply_markup=get_type_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_type)


@router.callback_query(F.data.startswith("type:"))
async def callback_type(callback: CallbackQuery, state: FSMContext):
    project_type = callback.data.split(":")[1]
    data = await state.get_data()
    ensure_data_dict(data)["type"] = project_type
    await state.update_data(data=data, step=3)
    
    if project_type == "file":
        await callback.message.edit_text(
            "Шаг 3/5: Выберите тип файла (или пропустите):",
            reply_markup=get_file_type_keyboard(),
        )
        await state.set_state(ProjectsStates.waiting_file_type)
    else:
        await callback.message.edit_text(
            "Шаг 3/5: Введите ID родительской папки (или /skip для пропуска):",
            reply_markup=get_back_keyboard(),
        )
        await state.set_state(ProjectsStates.waiting_parent_id)
    
    await callback.answer()


@router.callback_query(F.data.startswith("file_type:"))
async def callback_file_type(callback: CallbackQuery, state: FSMContext):
    file_type = callback.data.split(":")[1]
    data = await state.get_data()
    
    if file_type != "skip":
        ensure_data_dict(data)["file_type"] = file_type
    
    await state.update_data(data=data, step=4)
    
    await callback.message.edit_text(
        "Шаг 4/5: Введите ID родительской папки (или /skip для пропуска):",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_parent_id)
    await callback.answer()


@router.message(ProjectsStates.waiting_parent_id)
async def process_parent_id(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.text and message.text.strip().lower() == "/skip":
        ensure_data_dict(data).pop("parent_id", None)
        parent_id_text = "не указан"
    else:
        try:
            parent_id = int(message.text.strip())
            ensure_data_dict(data)["parent_id"] = parent_id
            parent_id_text = str(parent_id)
        except ValueError:
            await message.answer("❌ ID должен быть числом или /skip. Попробуйте еще раз:")
            return
    
    try:
        await message.edit_text(f"✅ Parent ID: {parent_id_text}")
    except Exception:
        await message.delete()
    
    await state.update_data(data=data, step=5)
    
    project_type = data.get("data", {}).get("type")
    file_type = data.get("data", {}).get("file_type")
    cmd_data = data.get("data", {})
    
    from handlers.commands.base import edit_or_send_message
    
    if project_type == "file" and file_type in ["readme", "architecture", "database", "swagger"]:
        text = (
            "➕ Создание проекта\n\n"
            f"✅ Name: {cmd_data.get('name')}\n"
            f"✅ Type: {cmd_data.get('type')}\n"
        )
        if cmd_data.get("file_type"):
            text += f"✅ File Type: {cmd_data.get('file_type')}\n"
        text += f"✅ Parent ID: {parent_id_text}\n\n"
        text += "Шаг 5/5: Отправьте файл для загрузки (или /skip для пропуска):\n\n"
        text += "Вы можете отправить файл или ввести URL в следующем сообщении."
        
        await edit_or_send_message(
            message.bot,
            state,
            message.chat.id,
            text,
            reply_markup=get_back_keyboard(),
        )
        await state.set_state(ProjectsStates.waiting_file)
    else:
        text = (
            "➕ Создание проекта\n\n"
            f"✅ Name: {cmd_data.get('name')}\n"
            f"✅ Type: {cmd_data.get('type')}\n"
        )
        if cmd_data.get("file_type"):
            text += f"✅ File Type: {cmd_data.get('file_type')}\n"
        text += f"✅ Parent ID: {parent_id_text}\n\n"
        text += "Шаг 5/5: Введите URL (или /skip для пропуска):"
        
        await edit_or_send_message(
            message.bot,
            state,
            message.chat.id,
            text,
            reply_markup=get_back_keyboard(),
        )
        await state.set_state(ProjectsStates.waiting_url)
    
    await state.update_data(data=data)


@router.message(ProjectsStates.waiting_file)
async def process_file(message: Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/skip":
        await message.answer(
            "Введите URL (или /skip для пропуска):",
            reply_markup=get_back_keyboard(),
        )
        await state.set_state(ProjectsStates.waiting_url)
        return
    
    if not message.document and not message.photo:
        await message.answer("❌ Пожалуйста, отправьте файл или фото, или введите /skip:")
        return
    
    data = await state.get_data()
    
    if message.document:
        file = await message.bot.get_file(message.document.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        file_content = file_bytes.read()
        extension = message.document.file_name.split(".")[-1] if message.document.file_name else "bin"
        content_type = message.document.mime_type or "application/octet-stream"
    elif message.photo:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        file_content = file_bytes.read()
        extension = "jpg"
        content_type = "image/jpeg"
    else:
        await message.answer("❌ Неподдерживаемый тип файла. Попробуйте еще раз:")
        return
    
    base64_content = base64.b64encode(file_content).decode("utf-8")
    
    data["file"] = {
        "name": "file",
        "extension": extension,
        "path": "",
        "content": base64_content,
    }
    ensure_data_dict(data)["filename"] = f"file.{extension}"
    ensure_data_dict(data)["content_type"] = content_type
    ensure_data_dict(data)["url"] = ""
    
    await state.update_data(data=data)
    
    await message.answer(
        "✅ Файл получен!\n\nВведите имя файла (без расширения) или /skip:",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_file_name)


@router.message(ProjectsStates.waiting_file_name)
async def process_file_name(message: Message, state: FSMContext):
    data = await state.get_data()
    file_info = data.get("file", {})
    
    if message.text and message.text.strip().lower() == "/skip":
        name = "file"
    else:
        name = message.text.strip() if message.text else "file"
    
    extension = file_info.get("extension", "bin")
    file_info["name"] = name
    data["file"] = file_info
    ensure_data_dict(data)["filename"] = f"{name}.{extension}"
    await state.update_data(data=data)
    
    await message.answer(
        "Введите путь для сохранения (или /skip для пропуска):",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_file_path)


@router.message(ProjectsStates.waiting_file_path)
async def process_file_path(message: Message, state: FSMContext):
    path = message.text.strip() if message.text and message.text != "/skip" else ""
    
    data = await state.get_data()
    file_info = data.get("file", {})
    file_info["path"] = path
    data["file"] = file_info
    await state.update_data(data=data)
    
    await send_command_with_file(message, state)


@router.message(ProjectsStates.waiting_url)
async def process_url(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.text and message.text.strip().lower() == "/skip":
        ensure_data_dict(data).pop("url", None)
        url_text = "не указан"
    else:
        url = message.text.strip() if message.text else ""
        if url:
            ensure_data_dict(data)["url"] = url
            url_text = url
        else:
            url_text = "не указан"
    
    try:
        await message.edit_text(f"✅ URL: {url_text}")
    except Exception:
        await message.delete()
    
    await state.update_data(data=data)
    
    from handlers.commands.base import edit_or_send_message
    cmd_data = data.get("data", {})
    preview_text = "📋 Предпросмотр данных:\n\n"
    preview_text += f"📝 Name: {cmd_data.get('name', 'N/A')}\n"
    preview_text += f"📁 Type: {cmd_data.get('type', 'N/A')}\n"
    if cmd_data.get("file_type"):
        preview_text += f"📄 File Type: {cmd_data.get('file_type')}\n"
    if cmd_data.get("parent_id"):
        preview_text += f"📂 Parent ID: {cmd_data.get('parent_id')}\n"
    preview_text += f"🔗 URL: {url_text}\n"
    preview_text += "\n⏳ Отправляю команду..."
    
    await edit_or_send_message(
        message.bot,
        state,
        message.chat.id,
        preview_text,
        reply_markup=None,
    )
    await send_command(message, state)


# Update Project
@router.callback_query(F.data == "cmd:projects:update_project")
async def callback_update_project(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="update_project", data={})
    await callback.message.edit_text(
        "✏️ Обновление проекта\n\nВведите ID проекта:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_project_id)
    await callback.answer()


@router.message(ProjectsStates.waiting_project_id)
async def process_project_id(message: Message, state: FSMContext):
    try:
        project_id = int(message.text)
        data = await state.get_data()
        ensure_data_dict(data)["id"] = project_id
        await state.update_data(data=data)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📝 Name", callback_data="update_field:name"),
                    InlineKeyboardButton(text="📁 Type", callback_data="update_field:type"),
                ],
                [
                    InlineKeyboardButton(text="📄 File Type", callback_data="update_field:file_type"),
                    InlineKeyboardButton(text="🔗 URL", callback_data="update_field:url"),
                ],
                [
                    InlineKeyboardButton(text="📂 Parent ID", callback_data="update_field:parent_id"),
                ],
                [
                    InlineKeyboardButton(text="✅ Готово", callback_data="update_field:done"),
                ],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
            ]
        )
        
        await message.answer(
            "Выберите поле для обновления или нажмите 'Готово' для отправки:",
            reply_markup=keyboard,
        )
        await state.set_state(ProjectsStates.waiting_update_field)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте еще раз:")


@router.callback_query(F.data.startswith("update_field:"))
async def callback_update_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]
    data = await state.get_data()
    
    if field == "done":
        cmd_data = ensure_data_dict(data)
        if not cmd_data or len(cmd_data) <= 1:
            await callback.answer("Выберите хотя бы одно поле для обновления", show_alert=True)
            return
        
        preview_text = "📋 Предпросмотр обновления:\n\n"
        for key, value in cmd_data.items():
            if key != "id":
                preview_text += f"  • {key}: {value}\n"
        preview_text += "\nОтправляю команду..."
        
        await callback.message.edit_text(preview_text)
        await send_command(callback.message, state)
        await callback.answer()
        return
    
    field_prompts = {
        "name": "Введите новое название:",
        "type": "Введите новый тип (folder/file):",
        "file_type": "Выберите тип файла:",
        "url": "Введите новый URL:",
        "parent_id": "Введите новый Parent ID (или /skip для удаления):",
    }
    
    if field == "file_type":
        await callback.message.edit_text(
            "Выберите тип файла:",
            reply_markup=get_file_type_keyboard(),
        )
        await state.update_data(current_field=field)
    else:
        await callback.message.edit_text(
            field_prompts.get(field, "Введите значение:"),
            reply_markup=get_cancel_keyboard(),
        )
        await state.update_data(current_field=field)
    
    await state.set_state(ProjectsStates.waiting_update_field)
    await callback.answer()


@router.callback_query(F.data.startswith("file_type:"))
async def callback_update_file_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора file_type при обновлении проекта"""
    current_state = await state.get_state()
    
    if current_state != ProjectsStates.waiting_update_field:
        await callback.answer("Неверный контекст", show_alert=True)
        return
    
    file_type = callback.data.split(":")[1]
    data = await state.get_data()
    
    if file_type != "skip":
        ensure_data_dict(data)["file_type"] = file_type
    else:
        ensure_data_dict(data).pop("file_type", None)
    
    data.pop("current_field", None)
    await state.update_data(data=data)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Name", callback_data="update_field:name"),
                InlineKeyboardButton(text="📁 Type", callback_data="update_field:type"),
            ],
            [
                InlineKeyboardButton(text="📄 File Type", callback_data="update_field:file_type"),
                InlineKeyboardButton(text="🔗 URL", callback_data="update_field:url"),
            ],
            [
                InlineKeyboardButton(text="📂 Parent ID", callback_data="update_field:parent_id"),
            ],
            [
                InlineKeyboardButton(text="✅ Готово", callback_data="update_field:done"),
            ],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )
    
    await callback.message.edit_text(
        f"✅ Поле 'file_type' обновлено.\n\nВыберите еще одно поле или нажмите 'Готово':",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.message(ProjectsStates.waiting_update_field)
async def process_update_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    current_field = data.get("current_field")
    
    if current_field == "type" and message.text not in ["folder", "file"]:
        await message.answer("❌ Тип должен быть 'folder' или 'file'. Попробуйте еще раз:")
        return
    
    if current_field == "parent_id":
        if message.text and message.text.strip().lower() == "/skip":
            ensure_data_dict(data).pop("parent_id", None)
        else:
            try:
                parent_id = int(message.text.strip())
                ensure_data_dict(data)["parent_id"] = parent_id
            except ValueError:
                await message.answer("❌ ID должен быть числом или /skip. Попробуйте еще раз:")
                return
    else:
        ensure_data_dict(data)[current_field] = message.text.strip()
    
    data.pop("current_field", None)
    await state.update_data(data=data)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Name", callback_data="update_field:name"),
                InlineKeyboardButton(text="📁 Type", callback_data="update_field:type"),
            ],
            [
                InlineKeyboardButton(text="📄 File Type", callback_data="update_field:file_type"),
                InlineKeyboardButton(text="🔗 URL", callback_data="update_field:url"),
            ],
            [
                InlineKeyboardButton(text="📂 Parent ID", callback_data="update_field:parent_id"),
            ],
            [
                InlineKeyboardButton(text="✅ Готово", callback_data="update_field:done"),
            ],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cmd:cancel")],
        ]
    )
    
    await message.answer(
        f"✅ Поле '{current_field}' обновлено.\n\nВыберите еще одно поле или нажмите 'Готово':",
        reply_markup=keyboard,
    )


# Delete Project
@router.callback_query(F.data == "cmd:projects:delete_project")
async def callback_delete_project(callback: CallbackQuery, state: FSMContext):
    await state.update_data(command_type="delete_project", data={})
    await callback.message.edit_text(
        "🗑️ Удаление проекта\n\nВведите ID проекта для удаления:",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(ProjectsStates.waiting_delete_id)
    await callback.answer()


@router.message(ProjectsStates.waiting_delete_id)
async def process_delete_id(message: Message, state: FSMContext):
    try:
        project_id = int(message.text)
        data = await state.get_data()
        ensure_data_dict(data)["id"] = project_id
        await state.update_data(data=data)
        await send_command(message, state)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте еще раз:")

