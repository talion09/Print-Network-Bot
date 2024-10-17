from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tgbot.handlers.users.start import admins_list, ru_language


async def about_loc(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    # text = _("Location")
    text = "Location"

    # await message.bot.send_location(message.from_user.id, latitude=, longitude=)
    await message.answer(text)


async def etwas(message: types.Message):
    db = message.bot.get('db')
    lala = await db.select_product(id=9)
    print(type(lala))


def register_adout(dp: Dispatcher):
    dp.register_message_handler(about_loc, text=["📍 Локация", "📍 Manzil"])
    dp.register_message_handler(etwas, Command("etwas"))
    dp.register_message_handler(etwas, content_types=types.ContentTypes.PHOTO)


