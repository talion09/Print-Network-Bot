from aiogram.dispatcher.filters.state import StatesGroup, State


class Regular(StatesGroup):
    Check = State()
    Name = State()
    Surname = State()
    Confirm = State()


class Appeal(StatesGroup):
    Text = State()
    Confirm = State()

