from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

adm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Продукты"),
            KeyboardButton(text="Админы")
        ],
        [
            KeyboardButton(text="Главное Меню")
        ]
    ], resize_keyboard=True)

confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Верно"),
            KeyboardButton(text="Отменить")

        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)