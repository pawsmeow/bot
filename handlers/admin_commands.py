from aiogram import Router, F, types
from config import ADMINS
from file_db import get_user_data, get_all_users
from keyboards.admin_filter import filter_keyboard, ALL_ROLES
from aiogram.fsm.context import FSMContext

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
        "Valhalla Gaming — это серия еженедельных соревновательных матчей, где каждый игрок получает шанс проявить себя, побороться за призы и прокачать рейтинг. Это твой путь к киберспортивному Олимпу!\n\n"
        "🔁 <b>Как проходит распределение игроков?</b>\n"
        "Участники распределяются по командам рандомайзером с учётом ранга.\n"
        "Это позволяет обеспечить честную игру и баланс между командами.\n\n"
        "🏆 <b>Как работает ранговая система?</b>\n"
        "Мы используем текущий ранг игрока для распределения по командам.\n"
        "Чем активнее и результативнее ты играешь — тем выше твой рейтинг.\n\n"
        "🎯 <b>Как начисляются баллы?</b>\n"
        "Баллы начисляются за ключевые игровые достижения:\n\n"
        "• Убийства (Kills)\n"
        "• Ассисты\n"
        "• KDA, Savage, другие значимые моменты\n"
        "• Победа в матче, вклад в команду\n\n"
        "Баллы влияют на твой общий рейтинг в системе Valhalla Gaming."
    )

    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "/rules")
async def rules(message: types.Message):
    text = (
        "📏 <b>Правила поведения участников Valhalla Gaming</b>\n\n"
        "🚫 <b>Запрещено:</b>\n"
        "• Оскорбления, мат и токсичное поведение (в игре, чате, голосе).\n"
        "• Оскорбления в адрес других игроков и админов.\n"
        "• Намеренный слив игр, неявка без предупреждения.\n"
        "• Использование читов, багов, макросов, стороннего ПО.\n"
        "• Флуд, спам, политические/религиозные провокации.\n"
        "• Обман или дезинформация игроков и администрации.\n\n"
        "✅ <b>Рекомендуется:</b>\n"
        "• Уважительно относиться к участникам и организаторам.\n"
        "• Подтверждать участие и быть вовремя на матчах.\n"
        "• Сообщать админам о нарушениях.\n"
        "• Поддерживать честную игру и помогать новичкам.\n\n"
        "🛡️ <b>Наказания:</b>\n"
        "• 1-е нарушение — предупреждение или минус рейтинг.\n"
        "• Повторные — временный бан.\n"
        "• Систематические — перманентный бан.\n\n"
        "🧾 Участвуя в матчах Valhalla Gaming, вы соглашаетесь с этими правилами. Незнание не освобождает от ответственности."
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.startswith("/sendall"))
async def sendall(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("У вас нет доступа.")
    text = message.text.replace("/sendall", "").strip()
    if not text:
        return await message.answer("Введите текст рассылки.")
    from file_db import users
    for uid in users.keys():
        try:
            await message.bot.send_message(uid, text)
        except:
            pass
    await message.answer("Рассылка отправлена.")


@router.message(F.text.startswith("/users"))
async def list_users(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ У вас нет доступа к этой команде.")

    args = message.text.strip().lower().split()[1:]
    users = get_all_users()
    if not users:
        return await message.answer("❌ Пользователей пока нет.")

    if args and args[0] == "count":
        servers_count = {"RU": 0, "KZ": 0, "KRG": 0, "UZB": 0}
        for data in users.values():
            s = data.get("server", "").upper()
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
    for uid, data in users.items():
        nickname = data.get("nickname", "неизвестно")
        game_id = data.get("game_id", "неизвестно")
        server = data.get("server", "неизвестно")
        roles = data.get("roles", [])
        role_list = ", ".join(roles)

        if server_filter and server != server_filter:
            continue
        if role_filters and not any(role in roles for role in role_filters):
            continue

        msg_lines.append(
            f"👤 <b>{nickname}</b>\n"
            f"🆔 <code>{game_id}</code>\n"
            f"🌍 Сервер: {server}\n"
            f"🎮 Роли: {role_list}\n"
            f"🔗 <a href='tg://user?id={uid}'>Профиль</a>\n"
            f"———"
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
    await callback.message.edit_reply_markup(reply_markup=filter_keyboard(selected_server=server, selected_roles=data.get("roles", [])))
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
    await callback.message.edit_reply_markup(reply_markup=filter_keyboard(selected_server=data.get("server"), selected_roles=selected))
    await callback.answer()

@router.callback_query(F.data == "filter_show")
async def show_filtered_users(callback: types.CallbackQuery, state: FSMContext):
    from file_db import get_all_users

    data = await state.get_data()
    server_filter = data.get("server")
    role_filters = data.get("roles", [])
    users = get_all_users()

    msg_lines = []
    for uid, u in users.items():
        if server_filter and u.get("server") != server_filter:
            continue
        if role_filters and not any(r in u.get("roles", []) for r in role_filters):
            continue
        msg_lines.append(
            f"👤 <b>{u.get('nickname')}</b>\n"
            f"🆔 <code>{u.get('game_id')}</code>\n"
            f"🌍 {u.get('server')} | 🎮 {', '.join(u.get('roles', []))}\n"
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