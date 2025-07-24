from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states import Register
from file_db import is_registered, register_user, delete_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_kb import server_keyboard, roles_keyboard
from config import ADMINS
from file_db import get_user_data
from aiogram import F, Router, types
from handlers.admin_commands import reglament, rules
router = Router()

@router.message(F.text == "/remove")
async def remove_profile_start(message: types.Message):
    if not is_registered(message.from_user.id):
        return await message.answer("У вас нет анкеты для удаления.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_remove"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_remove")
        ]
    ])
    await message.answer("⚠️ Вы уверены, что хотите удалить свою анкету? Это действие необратимо.", reply_markup=kb)


@router.callback_query(F.data == "confirm_remove")
async def confirm_remove(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    success = delete_user(user_id)

    if success:
        await callback.message.edit_text("✅ Ваша анкета удалена и помещена в архив.")
    else:
        await callback.message.edit_text("⚠️ Произошла ошибка при удалении.")

@router.callback_query(F.data == "cancel_remove")
async def cancel_remove(callback: types.CallbackQuery):
    await callback.message.edit_text("Удаление отменено.")
    
@router.message(F.text.startswith("/start"))
async def start(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=1)

    # Если пришёл аргумент /start rules или /start reglament
    if len(args) > 1:
        param = args[1].lower()
        if param == "reglament":
            await reglament(message)
            return
        elif param == "rules":
            await rules(message)
            return

    # Если пользователь уже зарегистрирован
    if is_registered(message.from_user.id):
        await message.answer("Вы уже зарегистрированы.")
    else:
        await state.set_state(Register.nickname)
        await message.answer("Введите ваш ник в игре:")
@router.message(Register.nickname)
async def get_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(Register.game_id)
    await message.answer("Введите ваш ID из игры:")

@router.message(Register.game_id)
async def get_game_id(message: types.Message, state: FSMContext):
    await state.update_data(game_id=message.text)
    await state.set_state(Register.server)
    await message.answer("Выберите ваш сервер:", reply_markup=server_keyboard())

@router.callback_query(F.data.startswith("server_"))
async def choose_server(callback: types.CallbackQuery, state: FSMContext):
    server = callback.data.split("_")[1].upper()
    await state.update_data(server=server)
    await state.set_state(Register.roles)
    await callback.message.edit_text("Выберите ваши роли (от 1 до 5):", reply_markup=roles_keyboard())

@router.callback_query(F.data.startswith("role_"))
async def toggle_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = data.get("roles", [])
    if role in selected:
        selected.remove(role)
    elif len(selected) < 5:
        selected.append(role)
    await state.update_data(roles=selected)
    await callback.message.edit_reply_markup(reply_markup=roles_keyboard(selected))

@router.callback_query(F.data == "roles_done")
async def finish_roles(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("roles"):
        await callback.answer("Выберите хотя бы одну роль", show_alert=True)
        return

    user_id = callback.from_user.id
    register_user(user_id, data)

    text = (
        f"Новая анкета:\n"
        f"👤 Ник: {data['nickname']}\n"
        f"🆔 ID: {data['game_id']}\n"
        f"🌍 Сервер: {data['server']}\n"
        f"🎮 Роли: {', '.join(data['roles'])}\n"
        f"🔗 Профиль: <a href='tg://user?id={user_id}'>Профиль</a>"
    )

    from keyboards.inline_kb import approval_keyboard
    for admin in ADMINS:
        await callback.bot.send_message(admin, text, parse_mode="HTML", reply_markup=approval_keyboard(user_id))

    await callback.message.edit_text("Анкета отправлена на проверку. Ожидайте ответа от админа.")
    await state.clear()


@router.message(F.text == "/profile")
async def profile(message: types.Message):
    user_id = message.from_user.id
    data = get_user_data(user_id)

    if not data:
        return await message.answer("Вы еще не заполнили анкету. Используйте /start, чтобы начать регистрацию.")

    text = (
        f"<b>🧾 Ваш профиль:</b>\n\n"
        f"👤 Ник: <b>{data.get('nickname')}</b>\n"
        f"🆔 ID из игры: <code>{data.get('game_id')}</code>\n"
        f"🌍 Сервер: {data.get('server')}\n"
        f"🎮 Роли: {', '.join(data.get('roles', []))}\n"
        f"🔗 Telegram: <a href='tg://user?id={user_id}'>Профиль</a>"
    )

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)