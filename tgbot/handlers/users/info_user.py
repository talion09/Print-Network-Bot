from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.main_menu import m_menu_uz, m_menu
from tgbot.keyboards.default.phone import phonenumber, phonenumber_uz
from tgbot.states.users import User


# User.Lang
async def info_lang(message: types.Message, state: FSMContext):
    if message.text == "🇷🇺 Ru":
        language = "🇷🇺 Ru"
        await message.answer("Введите название Вашего бренда")
        await state.update_data(lang=language)
        await User.Brend.set()
    elif message.text == "🇺🇿 Uz":
        language = "🇺🇿 Uz"
        await message.answer("Brend nomingizni kiriting")
        await state.update_data(lang=language)
        await User.Brend.set()
    else:
        await message.answer("Выберите язык:\n\nTilni tanlang:")


# User.Brend
async def info_brand(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("lang")
    await state.update_data(brand=message.text)
    if language == "🇷🇺 Ru":
        await message.answer("Введите Ваше Имя и Фамилию")
    else:
        await message.answer("To'liq ismingizni kiriting")
    await User.Name.set()


# User.Name
async def info_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("lang")
    await state.update_data(name=message.text)
    if language == "🇷🇺 Ru":
        await message.answer("Отправьте ваш номер телефона (998xxxxxxxxx):", reply_markup=phonenumber)
    else:
        await message.answer("Telefon raqamingizni yuboring (998xxxxxxxxx):", reply_markup=phonenumber_uz)
    await User.Phone.set()


# User.Phone
async def info_phone(message: types.Message, state: FSMContext):
    contc = message.contact.phone_number
    cont = contc[1:]
    await state.update_data(number=cont)
    await User.Next.set()
    await info_next(message, state)


# User.Phone
async def info_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("lang")
    try:
        int(message.text)
        if "9989" in str(message.text) and len(message.text) == 12:
            cont = message.text
            await state.update_data(number=cont)
            await User.Next.set()
            await info_next(message, state)
        else:
            if language == "🇷🇺 Ru":
                await message.answer("Отправьте ваш номер телефона (998xxxxxxxxx):", reply_markup=phonenumber)
            else:
                await message.answer("Telefon raqamingizni yuboring (998xxxxxxxxx):", reply_markup=phonenumber_uz)
            await User.Phone.set()
    except:
        if language == "🇷🇺 Ru":
            await message.answer("Отправьте ваш номер телефона (998xxxxxxxxx):", reply_markup=phonenumber)
        else:
            await message.answer("Telefon raqamingizni yuboring (998xxxxxxxxx):", reply_markup=phonenumber_uz)
        await User.Phone.set()


# User.Next
async def info_next(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    language = data.get("lang")
    number = data.get("number")
    brand = data.get("brand")
    name = data.get("name")
    username = message.from_user.username
    if language == "🇷🇺 Ru":
        await message.answer(
            f"{name}, Выберите что вас интересует:",
            reply_markup=m_menu)
        language = "ru"
    else:
        await message.answer(
            f"{name}, Sizni qiziqtirgan narsani tanlang:",
            reply_markup=m_menu_uz)
        language = "uz"

_user(
        brand=brand,
        name=name,
        username=username,
        telegram_id=int(message.from_user.id),
        number=int(number),
        language=language
    )

    await state.reset_state()


def register_info_user(dp: Dispatcher):
    dp.register_message_handler(info_lang, state=User.Lang)
    dp.register_message_handler(info_brand, state=User.Brend)
    dp.register_message_handler(info_name, state=User.Name)
    dp.register_message_handler(info_phone_text, state=User.Phone, content_types=types.ContentType.TEXT)
    dp.register_message_handler(info_phone, state=User.Phone, content_types=types.ContentType.CONTACT)
    dp.register_message_handler(info_next, state=User.Next)


