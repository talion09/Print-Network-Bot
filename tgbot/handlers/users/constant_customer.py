from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.users.start import admins_list, ru_language, bot_start
from tgbot.states.constant import Regular, Appeal


async def regular(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    text1 = _("Зарегистрироваться")
    text2 = _("Цены товаров")
    text3 = _("Что Вы хотите сделать?")
    # text1 = "Зарегистрироваться"
    # text2 = "Цены товаров"
    # text3 = "Что Вы хотите сделать?"
    markup.add(KeyboardButton(text=text1))
    markup.add(KeyboardButton(text=text2))
    await message.answer(text3, reply_markup=markup)


async def registr(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    await message.answer("TEXT")
    select = await db.select_user(telegram_id=int(message.from_user.id))
    name = select.get("brand")
    number = select.get("number")
    text1 = _("Бренд")
    text2 = _("Номер телефона")
    text3 = _("Все верно?")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    yes = _("Да ✅")
    custm = _("⚙️ Настройки")
    markup.insert(KeyboardButton(text=yes))
    markup.insert(KeyboardButton(text=custm))
    await message.answer(f"{text3}\n\n{text1}: {name}\n{text2}: {number}\n", reply_markup=markup)
    await Regular.Check.set()


# Regular.Check
async def registr_1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    surname = _("Введите Ваше Имя и Фамилию")
    await message.answer(surname)
    await Regular.Surname.set()


# Regular.Surname
async def registr_2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    if " " in str(message.text):
        await state.update_data(surname=message.text)
        select = await db.select_user(telegram_id=int(message.from_user.id))
        name = select.get("brand")
        number = select.get("number")
        text1 = _("Бренд")
        text2 = _("Номер телефона")
        surname = _("Имя и Фамилия")
        text3 = _("Все верно?")
        await message.answer(f"{text3}\n\n{text1}: {name}\n{text2}: {number}\n{surname}: {message.text}\n")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        yes = _("Да ✅")
        custm = _("⚙️ Настройки")
        markup.insert(KeyboardButton(text=yes))
        markup.insert(KeyboardButton(text=custm))
        await Regular.Confirm.set()
    else:
        surname = _("Введите Ваше Имя и Фамилию")
        await message.answer(surname)


# Regular.Confirm
async def registr_3(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    surname_db = data.get("surname")
    select = await db.select_user(telegram_id=int(message.from_user.id))
    name = select.get("brand")
    number = select.get("number")
    text1 = _("Бренд")
    text2 = _("Номер телефона")
    surname = _("Имя и Фамилия")
    for_worker = f"Анкета: \n\n" \
                 f"{text1}: {name}\n{text2}: {number}\n{surname}: {surname_db}"
    await message.bot.send_message(153479611, for_worker)

    text = _("Спасибо и тд")
    await message.answer(text)
    await bot_start(message, state)


async def diler(message: types.Message, state: FSMContext):
    await message.answer("TEXT")


async def appeal(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")

    await message.answer("TEXT")
    main_menu = _("Главное Меню")
    send_appeal = _("Отправьте свою жалобу или предложение")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.insert(KeyboardButton(text=main_menu))
    await message.answer(send_appeal, reply_markup=markup)
    await Appeal.Text.set()


# Appeal.Text
async def appeal_1(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")

    is_true = _("Все верно?")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    yes = _("Да ✅")
    custm = _("Нет ❌")
    markup.insert(KeyboardButton(text=yes))
    markup.insert(KeyboardButton(text=custm))
    await state.update_data(user_text=message.text)
    await message.answer(f"{is_true} \n\n{message.text}", reply_markup=markup)
    await Appeal.Confirm.set()


# Appeal.Confirm
async def appeal_2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    if message.text in ["Да ✅", "Ha ✅"]:
        data = await state.get_data()
        user_text = data.get("user_text")
        await message.bot.send_message(153479611, user_text)

        text = _("Спасибо и тд")
        await message.answer(text)
        await bot_start(message, state)
    elif message.text in ["Нет ❌", "Yo'q ❌"]:
        main_menu = _("Главное Меню")
        send_appeal = _("Отправьте свою жалобу или предложение")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.insert(KeyboardButton(text=main_menu))
        await message.answer(send_appeal, reply_markup=markup)
        await Appeal.Text.set()
    else:
        pass


def register_constant_customer(dp: Dispatcher):
    dp.register_message_handler(regular, text=["👤 Постоянный Клиент", "👤 Doimiy mijoz"])
    dp.register_message_handler(registr, text=["Зарегистрироваться", "Roʻyxatdan oʻtish"])
    dp.register_message_handler(registr_1, text=["Да ✅", "Ha ✅"], state=Regular.Check)
    dp.register_message_handler(registr_2, state=Regular.Surname)
    dp.register_message_handler(registr_3, text=["Да ✅", "Ha ✅"], state=Regular.Confirm)
    dp.register_message_handler(diler, text=["Дилер", "Diler"])
    dp.register_message_handler(appeal, text=["✉️ Жалоба и Предложение", "✉️ Shikoyat va Taklif"])
    dp.register_message_handler(appeal_1, state=Appeal.Text)
    dp.register_message_handler(appeal_2, state=Appeal.Confirm)







