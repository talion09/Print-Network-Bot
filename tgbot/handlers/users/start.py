from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.config import load_config
from tgbot.keyboards.default.language import lang
from tgbot.keyboards.default.main_menu import m_menu, admin_menu, m_menu_uz, admin_menu_uz
from tgbot.states.constant import Appeal
from tgbot.states.flayer import Del_Flayer, New_Flayer, Add_Flayer
from tgbot.states.portfel import Port, Order
from tgbot.states.users import User, Admin, Custom


async def canc(message):
    cancel = ReplyKeyboardMarkup(resize_keyboard=True)
    if await ru_language(message):
        cancel.add(KeyboardButton(text="Отменить"))
    else:
        cancel.add(KeyboardButton(text="Bekor qilish"))
    return cancel


async def ru_language(message):
    db = message.bot.get("db")
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    if user_in_db.get("language") == "ru":
        return True


async def admins_list(message):
    db = message.bot.get("db")
    admins_list = []
    for id, telegram_id, name in await db.select_all_admins():
        admins_list.append(telegram_id)
    if message.from_user.id in admins_list:
        if await ru_language(message):
            menu = admin_menu
        else:
            menu = admin_menu_uz
    else:
        if await ru_language(message):
            menu = m_menu
        else:
            menu = m_menu_uz
    return menu

    # config = load_config(".env")
    # ADMINS = config.tg_bot.admin_ids
    # if message.from_user.id in ADMINS:
    #     menu = admin_menu
    # else:
    #     menu = m_menu
    # return menu


async def bot_start(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await message.bot.send_message(153479611, f"{message.from_user.full_name} - {message.from_user.id}")
    await state.reset_state()
    try:
        user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
        menu = await admins_list(message)
        if user_in_db.get("language") == "ru":
            await message.answer(f"<b>{message.from_user.first_name}</b>, выберите что Вас интересует:", reply_markup=menu)
        else:
            await message.answer(f"<b>{message.from_user.first_name}</b>, Sizni qiziqtirgan narsani tanlang:", reply_markup=menu)
    except AttributeError:
        await message.answer(
            f"Здравствуйте! {message.from_user.full_name}\nВыберите язык:\n\nAssalomu alaykum!\nTilni tanlang:",
            reply_markup=lang)
        await User.Lang.set()


def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, CommandStart(), state="*")
    dp.register_message_handler(bot_start, text=["Главное Меню", "Asosiy menyu"])
    dp.register_message_handler(bot_start, text=["Главное Меню", "Asosiy menyu"], state=[Custom, Port, Order, Admin,
                                                                                         Add_Flayer, New_Flayer, Del_Flayer,
                                                                                         Appeal.Text])
