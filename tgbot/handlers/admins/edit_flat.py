from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ReplyKeyboardRemove

from tgbot.filters.is_admin import IsAdmin, IsAdmin_1
from tgbot.handlers.users.start import bot_start, admins_list
from tgbot.keyboards.default.cancel import cancel, back
from tgbot.keyboards.default.confirm import confirm
from tgbot.keyboards.inline.catalog import flat, delete_id
from tgbot.states.users import Admin, Add_Flat, Add_Room, Edit_flat


async def eddit_flat(message: types.Message):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Продажа"))
    markup.insert(KeyboardButton(text="Аренда"))
    markup.insert(KeyboardButton(text="Главное Меню"))
    await message.answer("Выберите категорию:", reply_markup=markup)
    await Edit_flat.Categ.set()


async def areas_rent(message, state, categ):
    db = message.bot.get("db")
    sub1categories = []
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Назад"))
    markup.insert(KeyboardButton(text="Продолжить"))
    for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_category(
            category=categ):
        if sub1category not in sub1categories:
            sub1categories.append(sub1category)
            markup.insert(KeyboardButton(text=sub1category))
    await state.update_data(categ=categ)
    await message.answer(f"Выберите район для редактирования или продолжите дальше", reply_markup=markup)
    await Edit_flat.Sub1.set()


async def rooms_rent(message, state, categ, sub1categ):
    db = message.bot.get("db")
    if message.text == "Назад":
        await state.reset_state()
        await eddit_flat(message)
    else:
        try:
            select = await db.select_flat(sub1category=sub1categ, category=categ)
            select.get("sub2category")
            sub2categories = []
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.insert(KeyboardButton(text="Назад"))
            markup.insert(KeyboardButton(text="Продолжить"))
            for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(
                    category=categ, sub1category=sub1categ):
                if sub2category not in sub2categories:
                    sub2categories.append(sub2category)
                    markup.insert(KeyboardButton(text=sub2category))
            await message.answer(f"Выберите количество комнат редактирования или продолжите дальше", reply_markup=markup)
            await state.update_data(sub1=sub1categ)
            await Edit_flat.Sub2.set()
        except:
            pass


# Edit_flat.Categ
async def select_in_categ(message: types.Message, state: FSMContext):
    await areas_rent(message, state, message.text)


# Edit_flat.Sub1
async def select_in_sub1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    if message.text == "Назад":
        await state.reset_state()
        await eddit_flat(message)
    elif message.text == "Продолжить":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        sub1categories = []
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_category(
                category=categ):
            if sub1category not in sub1categories:
                sub1categories.append(sub1category)
                markup.insert(KeyboardButton(text=sub1category))
        await state.update_data(categ=categ)
        await message.answer(f"Выберите район для редактирования", reply_markup=markup)
        await Edit_flat.Cont_Sub1.set()
    else:
        await rooms_rent(message, state, categ, message.text)


# Edit_flat.Sub2
async def select_in_sub2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    if message.text == "Назад":
        await areas_rent(message, state, categ)
    elif message.text == "Продолжить":
        sub2categories = []
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(
                category=categ, sub1category=sub1):
            if sub2category not in sub2categories:
                sub2categories.append(sub2category)
                markup.insert(KeyboardButton(text=sub2category))
        await message.answer(f"Выберите количество комнат для редактирования", reply_markup=markup)
        await Edit_flat.Cont_Sub2.set()
    else:
        try:
            select = await db.select_flat(sub2category=message.text)
            select.get("article_url")
            await state.reset_state()
            await message.answer("Выберите квартиру ссылку которой надо изменить", reply_markup=ReplyKeyboardRemove())
            for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in sorted(
                    await db.select_in_sub2category(category=categ, sub1category=sub1, sub2category=message.text)):
                inline_markup = InlineKeyboardMarkup(row_width=3)
                inline_markup.insert(InlineKeyboardButton(text=f"Изменить",
                                                          callback_data=delete_id.new(id=id, action="edit",
                                                                                      categ=categ)))
                inline_markup.insert(InlineKeyboardButton(text=f"Назад",
                                                          callback_data=delete_id.new(id=id, action="back_edit",
                                                                                      categ=categ)))
                await message.answer(article_url, reply_markup=inline_markup)
        except:
            pass


# ------------------------------------------------------------------------------------------------------------------------------------------------
# Edit_flat.Cont_Sub1
async def select_in_cont_sub1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    if message.text == "Назад":
        await areas_rent(message, state, categ)
    else:
        try:
            select = await db.select_flat(sub1category=message.text, category=categ)
            select.get("sub2category")
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.insert(KeyboardButton(text="Назад"))
            await message.answer(f"Введите новое название района '{message.text}' ", reply_markup=markup)
            await state.update_data(sub1=message.text)
            await Edit_flat.Cont2_Sub1.set()
        except:
            pass


# Edit_flat.Cont2_Sub1
async def select_in_cont2_sub1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    if message.text == "Назад":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        sub1categories = []
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_category(
                category=categ):
            if sub1category not in sub1categories:
                sub1categories.append(sub1category)
                markup.insert(KeyboardButton(text=sub1category))
        await state.update_data(categ=categ)
        await message.answer(f"Выберите район для редактирования", reply_markup=markup)
        await Edit_flat.Cont_Sub1.set()
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        select = await db.select_flat(sub1category=sub1, category=categ)
        sub1_uz = select.get("sub1category_uz")
        await state.update_data(sub1_uz=sub1_uz)
        await state.update_data(new_sub1=message.text)
        await message.answer(f"Введите новое название района '{sub1}' для узбекоязычных пользователей", reply_markup=markup)
        await Edit_flat.Cont2uz_Sub1.set()


# Edit_flat.Cont2uz_Sub1
async def select_in_cont2uz_sub1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub1_uz = data.get("sub1_uz")
    new_sub1 = data.get("new_sub1")
    if message.text == "Назад":
        select = await db.select_flat(sub1category=sub1, category=categ)
        select.get("sub2category")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        await message.answer(f"Введите новое название района '{sub1}' ", reply_markup=markup)
        await Edit_flat.Cont2_Sub1.set()
    else:
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(category=categ, sub1category=sub1):
            await db.update_flat(id=id, sub1category=new_sub1)
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category_uz(category=categ, sub1category_uz=sub1_uz):
            await db.update_flat(id=id, sub1category_uz=message.text)
        menu = await admins_list(message)
        await message.answer(f"Название района <b>{sub1}</b> изменился на:"
                             f"Рус: {new_sub1}"
                             f"Узб: {message.text}", reply_markup=menu)
        await state.reset_state()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# Edit_flat.Cont_Sub2
async def select_in_cont_sub2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    if message.text == "Назад":
        select = await db.select_flat(sub1category=sub1, category=categ)
        select.get("sub2category")
        sub2categories = []
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        markup.insert(KeyboardButton(text="Продолжить"))
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(
                category=categ, sub1category=sub1):
            if sub2category not in sub2categories:
                sub2categories.append(sub2category)
                markup.insert(KeyboardButton(text=sub2category))
        await message.answer(f"Выберите количество комнат редактирования или продолжите дальше", reply_markup=markup)
        await state.update_data(sub1=sub1)
        await Edit_flat.Sub2.set()
    else:
        try:
            select = await db.select_flat(sub2category=message.text, sub1category=sub1, category=categ)
            select.get("sub2category")
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.insert(KeyboardButton(text="Назад"))
            await state.update_data(sub2=message.text)
            await message.answer(f"Введите новое количество комнат", reply_markup=markup)
            await Edit_flat.Cont2_Sub2.set()
        except:
            pass


# Edit_flat.Cont2_Sub2
async def select_in_cont2_sub2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub2 = data.get("sub2")
    if message.text == "Назад":
        sub2categories = []
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(
                category=categ, sub1category=sub1):
            if sub2category not in sub2categories:
                sub2categories.append(sub2category)
                markup.insert(KeyboardButton(text=sub2category))
        await message.answer(f"Выберите количество комнат для редактирования", reply_markup=markup)
        await Edit_flat.Cont_Sub2.set()
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        select = await db.select_flat(sub2category=sub2, sub1category=sub1, category=categ)
        sub2_uz = select.get("sub2category_uz")
        sub1_uz = select.get("sub1category_uz")
        await state.update_data(sub2_uz=sub2_uz)
        await state.update_data(sub1_uz=sub1_uz)
        await state.update_data(new_sub2=message.text)
        await message.answer(f"Введите новое количество комнат для узбекоязычных пользователей", reply_markup=markup)
        await Edit_flat.Cont2uz_Sub2.set()


# Edit_flat.Cont2uz_Sub2
async def select_in_cont2uz_sub2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub2 = data.get("sub2")
    sub1_uz = data.get("sub1_uz")
    sub2_uz = data.get("sub2_uz")
    new_sub2 = data.get("new_sub2")
    if message.text == "Назад":
        select = await db.select_flat(sub2category=message.text, sub1category=sub1, category=categ)
        select.get("sub2category")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text="Назад"))
        await message.answer(f"Введите новое количество комнат", reply_markup=markup)
        await Edit_flat.Cont2_Sub2.set()
    else:
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub2category(category=categ,
                                                                                                                        sub1category=sub1,
                                                                                                                        sub2category=sub2):
            await db.update_flat(id=id, sub2category=new_sub2)
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub2category_uz(category=categ,
                                                                                                                        sub1category_uz=sub1_uz,
                                                                                                                        sub2category_uz=sub2_uz):
            await db.update_flat(id=id, sub2category_uz=message.text)
        menu = await admins_list(message)
        await message.answer(f"Название района <b>{sub1}</b> изменился на: \n"
                             f"Рус: {new_sub2} \n"
                             f"Узб: {message.text} \n", reply_markup=menu)
        await state.reset_state()
# ------------------------------------------------------------------------------------------------------------------------------------------------------------


async def edit_id_flat(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.message.bot.get("db")
    id = callback_data.get("id")
    select = await db.select_flat(id=int(id))
    categ = select.get("category")
    sub1 = select.get("sub1category")
    sub2 = select.get("sub2category")
    await call.answer()
    await call.message.answer("Отправьте новую ссылку на статью с квартирой", reply_markup=back)
    await Edit_flat.Cont_Sub3.set()
    await state.update_data(id=id)
    await state.update_data(categ=categ)
    await state.update_data(sub1=sub1)
    await state.update_data(sub2=sub2)


# Edit_flat.Cont_Sub3
async def edit1_id_flat(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    id = data.get("id")
    categ = data.get("categ")
    sub1 = data.get("sub1")
    sub2 = data.get("sub2")
    if message.text == "Назад":
        await state.reset_state()
        await message.answer("Выберите квартиру ссылку которой надо изменить", reply_markup=ReplyKeyboardRemove())
        for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in sorted(
                await db.select_in_sub2category(
                    category=categ, sub1category=sub1, sub2category=sub2)):
            inline_markup = InlineKeyboardMarkup(row_width=3)
            inline_markup.insert(InlineKeyboardButton(text=f"Изменить",
                                                      callback_data=delete_id.new(id=id, action="edit", categ=categ)))
            inline_markup.insert(InlineKeyboardButton(text=f"Назад",
                                                      callback_data=delete_id.new(id=id, action="back_edit",
                                                                                  categ=categ)))
            await message.answer(article_url, reply_markup=inline_markup)
    else:
        await message.answer("Отправьте новую ссылку на статью с квартирой для узбекоязычных пользователей", reply_markup=back)
        await Edit_flat.Contuz_Sub3.set()
        await state.update_data(url=message.text)


# Edit_flat.Contuz_Sub3
async def edit2_id_flat(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    if message.text == "Назад":
        await message.answer("Отправьте новую ссылку на статью с квартирой", reply_markup=back)
        await Edit_flat.Cont_Sub3.set()
    else:
        data = await state.get_data()
        id = int(data.get("id"))
        url = data.get("url")
        await db.update_flat(id=id, article_url=url)
        await db.update_flat(id=id, article_url_uz=message.text)
        await state.reset_state()
        menu = await admins_list(message)
        await message.answer(f"Название статья изменилась на: \n"
                             f"Рус: {url} \n")
        await message.answer(f"Название статья изменилась на: \n"
                             f"Узб: {message.text} \n", reply_markup=menu)


async def back_from_edit(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.message.bot.get("db")
    id = callback_data.get("id")
    select = await db.select_flat(id=int(id))
    categ = select.get("category")
    sub1 = select.get("sub1category")
    await call.answer()

    sub2categories = []
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.insert(KeyboardButton(text="Назад"))
    markup.insert(KeyboardButton(text="Продолжить"))
    for id, category, sub1category, sub1category_uz, sub2category, sub2category_uz, article_url, article_url_uz, like, dislike, viewed in await db.select_in_sub1category(
            category=categ, sub1category=sub1):
        if sub2category not in sub2categories:
            sub2categories.append(sub2category)
            markup.insert(KeyboardButton(text=sub2category))
    await call.message.answer(f"Выберите количество комнат редактирования или продолжите дальше", reply_markup=markup)
    await Edit_flat.Sub2.set()
    await state.update_data(categ=categ)
    await state.update_data(sub1=sub1)


def register_edit_flat(dp: Dispatcher):
    dp.register_message_handler(eddit_flat, IsAdmin(), text="Редактировать Квартиру")
    dp.register_message_handler(select_in_categ, IsAdmin(), state=Edit_flat.Categ, text=["Продажа", "Аренда"])
    dp.register_message_handler(select_in_sub1, state=Edit_flat.Sub1)
    dp.register_message_handler(select_in_sub2, state=Edit_flat.Sub2)

    dp.register_message_handler(select_in_cont_sub1, state=Edit_flat.Cont_Sub1)
    dp.register_message_handler(select_in_cont2_sub1, state=Edit_flat.Cont2_Sub1)
    dp.register_message_handler(select_in_cont2uz_sub1, state=Edit_flat.Cont2uz_Sub1)

    dp.register_message_handler(select_in_cont_sub2, state=Edit_flat.Cont_Sub2)
    dp.register_message_handler(select_in_cont2_sub2, state=Edit_flat.Cont2_Sub2)
    dp.register_message_handler(select_in_cont2uz_sub2, state=Edit_flat.Cont2uz_Sub2)

    dp.register_callback_query_handler(edit_id_flat, delete_id.filter(action="edit"), IsAdmin())
    dp.register_message_handler(edit1_id_flat, state=Edit_flat.Cont_Sub3)
    dp.register_message_handler(edit2_id_flat, state=Edit_flat.Contuz_Sub3)

    dp.register_callback_query_handler(back_from_edit, delete_id.filter(action="back_edit"),  IsAdmin())




