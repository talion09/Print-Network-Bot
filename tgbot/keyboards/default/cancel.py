from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отменить")
        ]
    ],
    resize_keyboard=True
)


phone_custom = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Поделиться контактом",
                           request_contact=True)
        ],
        [
            KeyboardButton(text="Отменить")
        ]
    ],
    resize_keyboard=True
)

phone_custom_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Raqamni yuborish",
                           request_contact=True)
        ],
        [
            KeyboardButton(text="Bekor qilish")
        ]
    ],
    resize_keyboard=True
)


