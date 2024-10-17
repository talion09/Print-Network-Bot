from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.filters.is_admin import IsAdmin
from tgbot.handlers.users.start import bot_start, admins_list
from tgbot.keyboards.default.admin_markp import back, confirm
from tgbot.keyboards.default.cust_flayer import flayer_customize
from tgbot.states.flayer import Add_Flayer, New_Flayer


async def custom_flayers(message: types.Message):
    await message.answer("Что вы хотите сделать ?", reply_markup=flayer_customize)


async def add_flayer(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.insert(KeyboardButton(text="💼 Портфолио"))
    markup.insert(KeyboardButton(text="📝 Заказать"))
    markup.insert(KeyboardButton(text="Другое"))
    markup.insert(KeyboardButton(text="Главное Меню"))
    markup.insert(KeyboardButton(text="Назад"))
    await message.answer("Выберите категорию:", reply_markup=markup)
    await Add_Flayer.Categ.set()


async def areas(message, state, categ):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Добавить подкатегорию"))
    markup.insert(KeyboardButton(text="Назад"))
    sub1categories = []
    for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
            await db.select_in_category(
                category=categ)):
        if sub1category not in sub1categories:
            sub1categories.append(sub1category)
            markup.add(KeyboardButton(text=sub1category))
    await state.update_data(categ=categ)
    await message.answer(f"Выберите подкатегорию либо добавьте новый", reply_markup=markup)
    await Add_Flayer.Sub1.set()


# Add_Flayer.Categ
async def select_in_categ(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.reset_state()
        await custom_flayers(message)
    else:
        await areas(message, state, message.text)


# Add_Flayer.Sub1
async def select_in_sub1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    if message.text == "Добавить подкатегорию":
        await message.answer("Отправьте название подкатегории для русскоязычных пользователей", reply_markup=back)
        await New_Flayer.New_sub1.set()
    elif message.text == "Назад":
        await state.reset_state()
        await add_flayer(message, state)
    else:
        try:
            select = await db.select_product(sub1category=message.text, category=categ)
            select.get("name")
            await message.answer(f"Отправьте название продукта для русскоязычных пользователей", reply_markup=back)
            await state.update_data(sub1=message.text)
            await Add_Flayer.Name.set()
        except:
            pass


# Add_Flayer.Name
async def add_fl_name(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    if message.text == "Назад":
        await areas(message, state, categ)
    else:
        await message.answer(f"Отправьте название продукта для узбекоязычных пользователей", reply_markup=back)
        await state.update_data(name=message.text)
        await Add_Flayer.Name_uz.set()


# Add_Flayer.Name_uz
async def add_fl_name_uz(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer(f"Отправьте название продукта для русскоязычных пользователей", reply_markup=back)
        await state.update_data(sub1=message.text)
        await Add_Flayer.Name.set()
    else:
        await message.answer(f"Отправьте фотки продукта", reply_markup=back)
        await state.update_data(name_uz=message.text)
        await Add_Flayer.Photos.set()


# Add_Flayer.Photos
async def add_fl_photos(message: types.Message, state: FSMContext):
    # Назад
    await message.answer("Отправьте название продукта для узбекоязычных пользователей", reply_markup=back)
    await Add_Flayer.Name_uz.set()


# Add_Flayer.Photos
async def add_fl_photoss(message: types.Message, state: FSMContext):
    # Фото
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Пoдтвердить"))
    await message.answer("Если есть ещё картинки, то отправляйте по-одному. \n Если нет, нажмите <b>Пoдтвердить</b>", reply_markup=markup)
    await Add_Flayer.Photos_2.set()
    photo = f"{message.photo[-1].file_id}"
    await state.update_data(photos=photo)


# Add_Flat.Photos_2
async def add_fl_photoss_2(message: types.Message, state: FSMContext):
    # Фото
    data = await state.get_data()
    photo = data.get("photos")
    print("photo",  photo)

    photos = photo.split(",")
    print("photos list ",  photos)
    photos.append(message.photo[-1].file_id)
    new_photos = ",".join(photos)
    print("new_photos str ",  new_photos)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Пoдтвердить"))
    await message.answer("Если есть ещё картинки, то отправляйте по-одному. \n Если нет, нажмите <b>Пoдтвердить</b>", reply_markup=markup)
    await Add_Flayer.Photos_2.set()
    await state.update_data(photos=new_photos)


# Add_Flat.Photos_2
async def add_fl_photos_2(message: types.Message, state: FSMContext):
    # Пoдтвердить
    db = message.bot.get("db")
    await state.update_data(url_uz=message.text)
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub1_db = await db.select_product(sub1category=sub1)
    sub1_uz = sub1_db.get("sub1category_uz")
    await state.update_data(sub1_uz=sub1_uz)
    name = data.get("name")
    name_uz = data.get("name_uz")
    photos = data.get("photos")
    text = f"Категория: {categ}\n" \
           f"Подкатегория: {sub1}\n" \
           f"Название: {name}/{name_uz}\n\n"
    await message.answer(text)

    media = types.MediaGroup()
    photos_id = photos.split(",")

    for i in photos_id:
        media.attach(types.InputMediaPhoto(i))
    await message.bot.send_media_group(chat_id=message.from_user.id, media=media)

    await message.answer("Все верно?", reply_markup=confirm)
    await Add_Flayer.Confirm.set()


# Add_Flayer.Confirm
async def add_fl_confirm(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    if message.text == "Верно":
        data = await state.get_data()
        categ = data.get("categ")
        sub1 = data.get("sub1")
        sub1_uz = data.get("sub1_uz")
        name = data.get("name")
        name_uz = data.get("name_uz")
        photos = data.get("photos")
        await db.add_product(category=categ, sub1category=sub1, sub1category_uz=sub1_uz, photos=photos, name=name, name_uz=name_uz)
        menu = await admins_list(message)
        await message.answer("Квартира была добавлена в базу данных!", reply_markup=menu)
        await state.reset_state()
    elif message.text == "Назад":
        await message.answer("Отправьте описание продукта для узбекоязычных пользователей", reply_markup=back)
        await Add_Flayer.Desc_uz.set()
    elif message.text == "Отменить":
        await state.reset_state()
        await add_flayer(message, state)
    else:
        pass


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# New_Flayer.New_sub1
async def new_sub1(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        data = await state.get_data()
        categ = data.get("categ")
        await areas(message, state, categ)
    else:
        await message.answer("Отправьте название подкатегории для узбекоязычных пользователей", reply_markup=back)
        await state.update_data(sub1=message.text)
        await New_Flayer.New_sub1_uz.set()


# New_Flayer.New_sub1_uz
async def new_sub1_uz(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Отправьте название подкатегории для русскоязычных пользователей")
        await New_Flayer.New_sub1.set()
    else:
        await message.answer(f"Отправьте название продукта для русскоязычных пользователей", reply_markup=back)
        await state.update_data(sub1_uz=message.text)
        await New_Flayer.New_Name.set()


# New_Flayer.New_Name
async def new_fl_name(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    if message.text == "Назад":
        await message.answer("Отправьте название подкатегории для узбекоязычных пользователей", reply_markup=back)
        await New_Flayer.New_sub1_uz.set()
    else:
        await message.answer(f"Отправьте название продукта для узбекоязычных пользователей", reply_markup=back)
        await state.update_data(name=message.text)
        await New_Flayer.New_Name_uz.set()


# New_Flayer.New_Name_uz
async def new_fl_name_uz(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer(f"Отправьте название продукта для русскоязычных пользователей", reply_markup=back)
        await state.update_data(sub1=message.text)
        await New_Flayer.New_Name.set()
    else:
        await message.answer(f"Отправьте фотки продукта", reply_markup=back)
        await state.update_data(name_uz=message.text)
        await New_Flayer.New_Photos.set()


# New_Flayer.New_Photos
async def new_fl_photos(message: types.Message, state: FSMContext):
    # Назад
    await message.answer("Отправьте название продукта для узбекоязычных пользователей", reply_markup=back)
    await New_Flayer.New_Name_uz.set()


# New_Flayer.New_Photos
async def new_fl_photoss(message: types.Message, state: FSMContext):
    # Фото
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Пoдтвердить"))
    await message.answer(
        "Если есть ещё картинки, то отправляйте по-одному. \n Если нет, нажмите <b>Пoдтвердить</b>",
        reply_markup=markup)
    await New_Flayer.New_Photos_2.set()
    photo = f"{message.photo[-1].file_id}"
    await state.update_data(photos=photo)


# New_Flayer.New_Photos_2
async def new_fl_photoss_2(message: types.Message, state: FSMContext):
    # Фото
    data = await state.get_data()
    photo = data.get("photos")
    print("photo", photo)

    photos = photo.split(",")
    print("photos list ", photos)
    photos.append(message.photo[-1].file_id)
    new_photos = ",".join(photos)
    print("new_photos str ", new_photos)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Пoдтвердить"))
    await message.answer(
        "Если есть ещё картинки, то отправляйте по-одному. \n Если нет, нажмите <b>Пoдтвердить</b>",
        reply_markup=markup)
    await New_Flayer.New_Photos_2.set()
    await state.update_data(photos=new_photos)


# New_Flayer.New_Photos_2
async def new_fl_photos_2(message: types.Message, state: FSMContext):
    # Пoдтвердить
    db = message.bot.get("db")
    await state.update_data(url_uz=message.text)
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub1_uz = data.get("sub1_uz")
    name = data.get("name")
    name_uz = data.get("name_uz")

    photos = data.get("photos")
    text = f"Категория: {categ}\n" \
           f"Подкатегория: {sub1}\n" \
           f"Название: {name}/{name_uz}\n\n"
    await message.answer(text)

    media = types.MediaGroup()
    photos_id = photos.split(",")

    for i in photos_id:
        media.attach(types.InputMediaPhoto(i))
    await message.bot.send_media_group(chat_id=message.from_user.id, media=media)

    await message.answer("Все верно?", reply_markup=confirm)
    await New_Flayer.New_Confirm.set()


# New_Flayer.New_Confirm
async def new_fl_confirm(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    if message.text == "Верно":
        data = await state.get_data()
        categ = data.get("categ")
        sub1 = data.get("sub1")
        sub1_uz = data.get("sub1_uz")
        name = data.get("name")
        name_uz = data.get("name_uz")
        photos = data.get("photos")
        await db.add_product(category=categ, sub1category=sub1, sub1category_uz=sub1_uz, photos=photos, name=name,
                             name_uz=name_uz)
        menu = await admins_list(message)
        await message.answer("Квартира была добавлена в базу данных!", reply_markup=menu)
        await state.reset_state()
    elif message.text == "Назад":
        await message.answer("Отправьте описание продукта для узбекоязычных пользователей", reply_markup=back)
        await New_Flayer.New_Desc_uz.set()
    elif message.text == "Отменить":
        await state.reset_state()
        await add_flayer(message, state)
    else:
        pass


def register_custom_flat(dp: Dispatcher):
    dp.register_message_handler(custom_flayers, IsAdmin(), text="Продукты")
    dp.register_message_handler(add_flayer, IsAdmin(), text="Добавить")
    dp.register_message_handler(select_in_categ, IsAdmin(), state=Add_Flayer.Categ, text=["💼 Портфолио", "📝 Заказать", "Другое", "Назад"])
    dp.register_message_handler(select_in_sub1, state=Add_Flayer.Sub1)
    dp.register_message_handler(add_fl_name, state=Add_Flayer.Name)
    dp.register_message_handler(add_fl_name_uz, state=Add_Flayer.Name_uz)
    dp.register_message_handler(add_fl_photos, state=Add_Flayer.Photos, text="Назад")
    dp.register_message_handler(add_fl_photoss, state=Add_Flayer.Photos, content_types=types.ContentTypes.PHOTO)
    dp.register_message_handler(add_fl_photos_2, state=Add_Flayer.Photos_2, text="Пoдтвердить")
    dp.register_message_handler(add_fl_photoss_2, state=Add_Flayer.Photos_2, content_types=types.ContentTypes.PHOTO)
    dp.register_message_handler(add_fl_confirm, state=Add_Flayer.Confirm)

    dp.register_message_handler(new_sub1, state=New_Flayer.New_sub1)
    dp.register_message_handler(new_sub1_uz, state=New_Flayer.New_sub1_uz)
    dp.register_message_handler(new_fl_name, state=New_Flayer.New_Name)
    dp.register_message_handler(new_fl_name_uz, state=New_Flayer.New_Name_uz)
    dp.register_message_handler(new_fl_photos, state=New_Flayer.New_Photos, text="Назад")
    dp.register_message_handler(new_fl_photoss, state=New_Flayer.New_Photos, content_types=types.ContentTypes.PHOTO)
    dp.register_message_handler(new_fl_photos_2, state=New_Flayer.New_Photos_2, text="Пoдтвердить")
    dp.register_message_handler(new_fl_photoss_2, state=New_Flayer.New_Photos_2, content_types=types.ContentTypes.PHOTO)
    dp.register_message_handler(new_fl_confirm, state=New_Flayer.New_Confirm)








