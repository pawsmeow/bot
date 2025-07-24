from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import ADMINS
from database import get_user, get_all_users
from keyboards.admin_filter import filter_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await callback.message.edit_text("✅ Анкета принята")
    await callback.bot.send_message(user_id, "Ваша анкета принята!")

@router.callback_query(F.data.startswith("reject_"))
async def reject(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await callback.message.edit_text("❌ Анкета отклонена")
    await callback.bot.send_message(user_id, "Ваша анкета отклонена.")

@router.message(F.text.startswith("/reglament"))
async def reglament(message: types.Message):
    text = (
        "📜 <b>Регламент участия в матчах Valhalla Gaming</b>\n\n"
        "❓ <b>Что такое Valhalla Gaming?</b>\n"
        "Valhalla Gaming — это серия еженедельных соревновательных матчей...\n"
        "🔁 <b>Как проходит распределение игроков?</b>\n"
        "Участники распределяются по командам рандомайзером...\n"
        "🏆 <b>Как работает ранговая система?</b>\n"
        "🎯 <b>Как начисляются баллы?</b>\n"
        "• Убийства (Kills)\n• Ассисты\n• Победа в матче...\n"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "/rules")
async def rules(message: types.Message):
    text = (
        "📏 <b>Правила поведения участников Valhalla Gaming</b>\n\n"
        "🚫 <b>Запрещено:</b>\n• Токсичность\n• Читы\n• Обман\n\n"
        "✅ <b>Рекомендуется:</b>\n• Уважение\n• Честная игра\n\n"
        "🛡️ <b>Наказания:</b>\n• Варны, баны и пермабаны\n"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text.startswith("/sendall"))
async def sendall(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("У вас нет доступа.")
    text = message.text.replace("/sendall", "").strip()
    if not text:
        return await message.answer("Введите текст рассылки.")

    users = get_all_users()
    for user in users:
        try:
            await message.bot.send_message(user["telegram_id"], text)
        except:
            pass
    await message.answer("Рассылка отправлена.")

@router.message(F.text.startswith("/users"))
async def list_users(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ У вас нет доступа к этой команде.")

    args = message.text.strip().lower().split()[1:]
    all_users = get_all_users()
    if not all_users:
        return await message.answer("❌ Пользователей пока нет.")

    if args and args[0] == "count":
        servers_count = {"RU": 0, "KZ": 0, "KRG": 0, "UZB": 0}
        for user in all_users:
            s = user.get("server", "").upper()
            if s in servers_count:
                servers_count[s] += 1
        total = sum(servers_count.values())
        text = "\n".join([f"{k}: {v}" for k, v in servers_count.items()])
        text += f"\n\n<b>Всего: {total}</b>"
        return await message.answer(text, parse_mode="HTML")

    server_filter = None
    role_filters = []

    for arg in args:
        upper = arg.upper()
        if upper in ["RU", "KZ", "KRG", "UZB"]:
            server_filter = upper
        else:
            role_filters.append(arg.capitalize())

    msg_lines = []
    for user in all_users:
        uid = user["telegram_id"]
        roles = user.get("role", "")
        role_list = roles

        if server_filter and user.get("server") != server_filter:
            continue
        if role_filters and all(r not in roles for r in role_filters):
            continue

        msg_lines.append(
            f"👤 <b>{user.get('nickname')}</b>\n"
            f"🆔 <code>{user.get('game_id')}</code>\n"
            f"🌍 Сервер: {user.get('server')}\n"
            f"🎮 Роли: {role_list}\n"
            f"🔗 <a href='tg://user?id={uid}'>Профиль</a>\n———"
        )

    if not msg_lines:
        return await message.answer("❌ Пользователей с такими фильтрами не найдено.")

    MAX_LENGTH = 4000
    text = ""
    for line in msg_lines:
        if len(text) + len(line) >= MAX_LENGTH:
            await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
            text = ""
        text += line + "\n"
    if text:
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@router.message(F.text == "/filter_users")
async def show_filter_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ У вас нет доступа.")
    await state.update_data(server=None, roles=[])
    await message.answer("Выберите фильтры:", reply_markup=filter_keyboard())

@router.callback_query(F.data.startswith("filter_server_"))
async def toggle_server(callback: types.CallbackQuery, state: FSMContext):
    server = callback.data.split("_")[-1]
    await state.update_data(server=server)
    data = await state.get_data()
    await callback.message.edit_reply_markup(
        reply_markup=filter_keyboard(selected_server=server, selected_roles=data.get("roles", [])))
    await callback.answer()

@router.callback_query(F.data.startswith("filter_role_"))
async def toggle_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.split("_")[-1]
    data = await state.get_data()
    selected = data.get("roles", [])
    if role in selected:
        selected.remove(role)
    else:
        selected.append(role)
    await state.update_data(roles=selected)
    await callback.message.edit_reply_markup(
        reply_markup=filter_keyboard(selected_server=data.get("server"), selected_roles=selected))
    await callback.answer()

@router.callback_query(F.data == "filter_show")
async def show_filtered_users(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    server_filter = data.get("server")
    role_filters = data.get("roles", [])
    users = get_all_users()

    msg_lines = []
    for user in users:
        uid = user["telegram_id"]
        if server_filter and user.get("server") != server_filter:
            continue
        if role_filters and all(r not in user.get("role", "") for r in role_filters):
            continue
        msg_lines.append(
            f"👤 <b>{user.get('nickname')}</b>\n"
            f"🆔 <code>{user.get('game_id')}</code>\n"
            f"🌍 {user.get('server')} | 🎮 {user.get('role')}\n"
            f"🔗 <a href='tg://user?id={uid}'>Профиль</a>\n———"
        )

    if not msg_lines:
        return await callback.message.answer("❌ Нет пользователей с такими фильтрами.")

    text = ""
    MAX = 4000
    for line in msg_lines:
        if len(text) + len(line) > MAX:
            await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
            text = ""
        text += line + "\n"
    if text:
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

    await callback.answer()
