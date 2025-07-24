from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ALL_SERVERS = ["RU", "KZ", "KRG", "UZB"]
ALL_ROLES = ["Мид", "Голд", "Лес", "Эксп", "Роум"]

def filter_keyboard(selected_server=None, selected_roles=None):
    selected_roles = selected_roles or []
    keyboard = []

    # Сервера
    row = []
    for server in ALL_SERVERS:
        prefix = "✅ " if server == selected_server else ""
        row.append(InlineKeyboardButton(text=prefix + server, callback_data=f"filter_server_{server}"))
    keyboard.append(row)

    # Роли (по 2 в ряд)
    for i in range(0, len(ALL_ROLES), 2):
        row = []
        for role in ALL_ROLES[i:i+2]:
            prefix = "✅ " if role in selected_roles else ""
            row.append(InlineKeyboardButton(text=prefix + role, callback_data=f"filter_role_{role}"))
        keyboard.append(row)

    # Показать
    keyboard.append([InlineKeyboardButton(text="📋 Показать", callback_data="filter_show")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
