from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.users.start import admins_list, ru_language, canc, bot_start
from tgbot.keyboards.default.cancel import phone_custom, phone_custom_uz
from tgbot.states.constant import Regular
from tgbot.states.users import Custom


async def about_user(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    await state.reset_state()
    select = await db.select_user(telegram_id=int(message.from_user.id))
    name = select.get("brand")
    number = select.get("number")
    language = select.get("language")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    text1 = _("Бренд")
    text2 = _("Номер телефона")
    text3 = _("Язык")
    text4 = _("Назад")
    markup.insert(KeyboardButton(text=text1))
    markup.insert(KeyboardButton(text=text2))
    markup.insert(KeyboardButton(text=text3))
    markup.insert(KeyboardButton(text=text4))
    await message.answer(f"{text1}: {name}\n{text2}: {number}\n{text3}: {language}", reply_markup=markup)


async def name1(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")
    cancel = await canc(message)
    text1 = _("Введите название Вашего бренда:")
    await message.answer(text1, reply_markup=cancel)
    await Custom.Name.set()


async def phone1(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")
    text1 = _("Отправьте ваш номер телефона (998xxxxxxxxx):")
    if await ru_language(message):
        phone = phone_custom
    else:
        phone = phone_custom_uz
    await message.answer(text1, reply_markup=phone)
    await Custom.Phone.set()


async def language1(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")
    text1 = _("Отменить")
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 Uz"),
                   KeyboardButton(text="🇷🇺 Ru")]], resize_keyboard=True)
    markup.add(KeyboardButton(text=text1))
    text2 = _("Выберите язык:")
    await message.answer(text2, reply_markup=markup)
    await Custom.Lang.set()


async def cancel1(message: types.Message, state: FSMContext):
    await bot_start(message, state)


# Custom.Name
async def name(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    text1 = _("Отменить")
    text2 = _("Изменение отменено")
    text3 = _("Успешно изменено")
    # text4 = _("Введите название Вашего бренда:")
    if message.text == text1:
        await state.reset_state()
        await message.answer(text2)
        await about_user(message, state)
    else:
        await db.update_user(telegram_id=int(message.from_user.id), brand=message.text)
        await state.reset_state()
        await message.answer(text3)
        await about_user(message, state)
    # else:
    #     cancel = await canc(message)
    #     await message.answer(text4, reply_markup=cancel)
    #     await Custom.Name.set()


# Custom.Phone
async def phone(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    contc = message.contact.phone_number
    # cont = contc[1:]
    text3 = _("Успешно изменено")
    await db.update_user(telegram_id=int(message.from_user.id), number=int(contc))
    await state.reset_state()
    await message.answer(text3)
    await about_user(message, state)


# Custom.Phone
async def phone_text(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    text1 = _("Отменить")
    text2 = _("Изменение отменено")
    text3 = _("Успешно изменено")
    text4 = _("📞 Отправить Мой контакт")
    text5 = _("Отправьте ваш номер телефона (998xxxxxxxxx):")

    if message.text == text1:
        await state.reset_state()
        await message.answer(text2)
        await about_user(message, state)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(text=text4, request_contact=True))
        markup.add(KeyboardButton(text=text1))
        try:
            int(message.text)
            if "9989" in str(message.text) and len(message.text) == 12:
                cont = message.text
                await db.update_user(telegram_id=int(message.from_user.id), number=int(cont))
                await state.reset_state()
                await message.answer(text3)
                await about_user(message, state)
            else:
                await message.answer(text5, reply_markup=markup)
                await Custom.Phone.set()
        except:
            await message.answer(text5, reply_markup=markup)
            await Custom.Phone.set()


# Custom.Lang
async def language(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    menu = await admins_list(message)

    text1 = _("Отменить")
    text2 = _("Изменение отменено")
    text3 = _("Выберите язык:")

    if message.text == text1:
        await state.reset_state()
        await message.answer(text2)
        await about_user(message, state)
    elif message.text == "🇺🇿 Uz":
        await db.update_user(telegram_id=int(message.from_user.id), language="uz")
        await message.answer("Muvaffaqiyatli o'zgartirildi")
        await bot_start(message, state)
    elif message.text == "🇷🇺 Ru":
        await db.update_user(telegram_id=int(message.from_user.id), language="ru")
        await message.answer("Успешно изменено", reply_markup=menu)
        await bot_start(message, state)
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🇺🇿 Uz"),
                       KeyboardButton(text="🇷🇺 Ru")]], resize_keyboard=True)
        markup.add(KeyboardButton(text=text1))
        await message.answer(text=text3, reply_markup=markup)
        await Custom.Lang.set()


def register_custom(dp: Dispatcher):
    dp.register_message_handler(about_user, text=["⚙️ Настройки", "⚙️ Sozlamalar"])
    dp.register_message_handler(about_user, text=["⚙️ Настройки", "⚙️ Sozlamalar"], state=[Regular.Check, Regular.Confirm])
    dp.register_message_handler(name1, text=["Бренд", "Brand"])
    dp.register_message_handler(phone1, text=["Номер телефона", "Telefon raqami"])
    dp.register_message_handler(language1, text=["Язык", "Til"])
    dp.register_message_handler(cancel1, text=["Назад", "Ortga"])

    dp.register_message_handler(name, state=Custom.Name)
    dp.register_message_handler(phone_text, state=Custom.Phone, content_types=types.ContentType.TEXT)
    dp.register_message_handler(phone, state=Custom.Phone, content_types=types.ContentType.CONTACT)
    dp.register_message_handler(language, state=Custom.Lang)
