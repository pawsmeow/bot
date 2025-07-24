from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def server_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="server_ru")],
        [InlineKeyboardButton(text="🇰🇿 KZ", callback_data="server_kz")],
        [InlineKeyboardButton(text="🇰🇬 KRG", callback_data="server_krg")],
        [InlineKeyboardButton(text="🇺🇿 UZB", callback_data="server_uzb")]
    ])

ROLES = ["Лес", "Мид", "Голд", "Эксп", "Роум"]

def roles_keyboard(selected=None):
    selected = selected or []
    buttons = [
        InlineKeyboardButton(
            text=("✅ " if role in selected else "") + role,
            callback_data=f"role_{role}"
        ) for role in ROLES
    ]
    rows = [[b] for b in buttons]
    rows.append([InlineKeyboardButton(text="✅ Готово", callback_data="roles_done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def approval_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])
