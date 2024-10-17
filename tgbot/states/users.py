from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    Lang = State()
    Brend = State()
    Name = State()
    Phone = State()
    Next = State()

    Cart = State()



class Custom(StatesGroup):
    Lang = State()
    Name = State()
    Phone = State()


class Admin(StatesGroup):
    Delete_admin = State()
    Add_admin = State()





