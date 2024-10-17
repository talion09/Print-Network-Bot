from aiogram.dispatcher.filters.state import StatesGroup, State


class Port(StatesGroup):
    Sub1 = State()
    Lift = State()


class Order(StatesGroup):
    Sub1 = State()
    Lift = State()
    Sub2 = State()