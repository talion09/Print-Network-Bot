from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

flayer_customize = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить"),
            KeyboardButton(text="Удалить"),
        ],
        [
            KeyboardButton(text="Главное Меню")
        ]
    ],
    resize_keyboard=True
)

