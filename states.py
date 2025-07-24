from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    nickname = State()
    game_id = State()
    server = State()
    roles = State()
