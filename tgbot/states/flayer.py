from aiogram.dispatcher.filters.state import StatesGroup, State


class Add_Flayer(StatesGroup):
    Categ = State()
    Sub1 = State()
    Name = State()
    Name_uz = State()
    Photos = State()
    Photos_2 = State()
    Confirm = State()


class New_Flayer(StatesGroup):
    New_sub1 = State()
    New_sub1_uz = State()
    New_Name = State()
    New_Name_uz = State()
    New_Desc = State()
    New_Desc_uz = State()
    New_Photos = State()
    New_Photos_2 = State()
    New_Confirm = State()


class Del_Flayer(StatesGroup):
    Categ = State()
    Sub1 = State()
    Lift = State()