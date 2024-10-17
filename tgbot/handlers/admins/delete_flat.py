import math

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.filters.is_admin import IsAdmin
from tgbot.handlers.admins.custom_flat import custom_flayers
from tgbot.states.flayer import Del_Flayer


async def del_flayer(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.insert(KeyboardButton(text="💼 Портфолио"))
    markup.insert(KeyboardButton(text="📝 Заказать"))
    markup.insert(KeyboardButton(text="Другое"))
    markup.insert(KeyboardButton(text="Главное Меню"))
    markup.insert(KeyboardButton(text="Назад"))
    await message.answer("Выберите категорию:", reply_markup=markup)
    await Del_Flayer.Categ.set()


async def del_areas(message, state, categ):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    sub1categories = []
    for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
            await db.select_in_category(
                category=categ)):
        if sub1category not in sub1categories:
            sub1categories.append(sub1category)
            markup.add(KeyboardButton(text=sub1category))
    markup.insert(KeyboardButton(text="Назад"))
    await state.update_data(categor=categ)
    await message.answer(f"Выберите подкатегорию", reply_markup=markup)
    await Del_Flayer.Sub1.set()


# Del_Flayer.Categ
async def select_in_categ(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.reset_state()
        await custom_flayers(message)
    else:
        await del_areas(message, state, message.text)


# Del_Flayer.Sub1
async def get_order_sub1category(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    data = await state.get_data()
    categ = data.get("categor")

    main = "Главное Меню"
    back = "Назад"
    another = "Другое"

    if message.text == back:
        await state.reset_state()
        await del_flayer(message, state)
    else:
        products = []
        send_text = "Категория"
        await state.update_data(sub1=message.text)

        try:
            select = await db.select_product(sub1category=message.text)
            sub1 = select.get("sub1category")

            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_sub1category(
                            category=categ, sub1category=sub1), reverse=True):
                if id not in products:
                    products.append(id)

            sliced = products[0:3]
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            divider = len(products) / 3
            max_pages = math.ceil(divider)
            if max_pages > 1:
                back_page = KeyboardButton(text=f"...")
                pages = KeyboardButton(text=f"1/{max_pages}")
                next = KeyboardButton(text=f"»»»")
                row = [back_page, pages, next]
                markup.row(*row)

            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            for item_id in sliced:

                select = await db.select_product(id=item_id)
                name = select.get("name")
                photos = select.get("photos")

                caption = f"<b>{name}</b>"
                product_cart = f"Удалить из Базы Данных {name}"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)

                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                markup.add(KeyboardButton(text=product_cart))

            await message.answer(f"{send_text} <b>{message.text}</b>", reply_markup=markup)
            await Del_Flayer.Lift.set()
            await state.update_data(main_catg=categ)
            await state.update_data(catg=sub1)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=3)
            await state.update_data(page=1)
        except:
            pass


# Del_Flayer.Lift
async def lift_catg_next_order(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")
    max_pages = data.get("max_pages")
    quant = data.get("quant")
    page = data.get("page")

    main = "Главное Меню"
    back = "Назад"
    send_text = "Продукты в категории"

    if message.text == back:
        await state.reset_state()
        await del_areas(message, state, main_catg)
    elif message.text == "»»»":
        if int(page) == int(max_pages):
            pass
        else:
            if int(page) + 1 == max_pages:
                next = KeyboardButton(text=f"...")
                back_page = KeyboardButton(text=f"«««")
            else:
                next = KeyboardButton(text=f"»»»")
                back_page = KeyboardButton(text=f"«««")

            items = []
            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_sub1category(
                        category=main_catg, sub1category=catg), reverse=True):
                items.append(id)

            quant_plus = int(quant) + 3
            sliced = items[int(quant):quant_plus]

            pages = KeyboardButton(text=f"{int(page) + 1}/{max_pages}")
            row = [back_page, pages, next]

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.row(*row)
            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            for item_id in sliced:
                select = await db.select_product(id=item_id)
                name = select.get("name")
                photos = select.get("photos")

                caption = f"<b>{name}</b>"
                product_cart = f"Удалить из Базы Данных {name}"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)
                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                markup.add(KeyboardButton(text=product_cart))

            await message.answer(f"{send_text} <b>{catg}</b>", reply_markup=markup)
            await Del_Flayer.Lift.set()
            await state.update_data(main_catg=main_catg)
            await state.update_data(catg=catg)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=quant_plus)
            await state.update_data(page=int(page) + 1)


# Del_Flayer.Lift
async def lift_catg_back_order(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")
    max_pages = data.get("max_pages")
    quant = data.get("quant")
    page = data.get("page")

    main = "Главное Меню"
    back = "Назад"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    send_text = "Продукты в категории"

    if 1 == int(page):
        pass
    else:
        if 0 < int(page) <= int(max_pages):
            pass

        if int(page) - 1 == 1:
            next = KeyboardButton(text=f"»»»")
            back_page = KeyboardButton(text=f"...")
        else:
            next = KeyboardButton(text=f"»»»")
            back_page = KeyboardButton(text=f"«««")

        items = []
        for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                await db.select_in_sub1category(
                    category=main_catg, sub1category=catg), reverse=True):
            items.append(id)

        quant_minus = int(quant) - 6
        quant_new = int(quant) - 3
        sliced = items[quant_minus:quant_new]
        pages = KeyboardButton(text=f"{int(page) - 1}/{max_pages}")
        row = [back_page, pages, next]

        markup.row(*row)
        markup.insert(KeyboardButton(text=main))
        markup.insert(KeyboardButton(text=back))
        for item_id in sliced:
            select = await db.select_product(id=item_id)
            name = select.get("name")
            photos = select.get("photos")

            caption = f"<b>{name}</b>"
            product_cart = f"Удалить из Базы Данных {name}"

            media = types.MediaGroup()
            photos_id = photos.split(",")
            last = photos_id[-1]
            photos_id.remove(last)
            for i in photos_id:
                media.attach(types.InputMediaPhoto(i))
            media.attach(types.InputMediaPhoto(last, caption))
            await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
            markup.add(KeyboardButton(text=product_cart))

        await message.answer(f"{send_text} <b>{catg}</b>", reply_markup=markup)
        await Del_Flayer.Lift.set()
        await state.update_data(main_catg=main_catg)
        await state.update_data(catg=catg)
        await state.update_data(max_pages=max_pages)
        await state.update_data(quant=quant_new)
        await state.update_data(page=int(page) - 1)


# Del_Flayer.Lift
async def add_cart(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")

    main = "Главное Меню"
    back = "Назад"

    if "Удалить из Базы Данных " in message.text:
        del_name = message.text[23:]
        try:
            select = await db.select_product_in_sub1category(category=main_catg, sub1category=catg, name=del_name)
            id = select.get("id")
            await db.delete_product(id=int(id))
            await db.delete_in_cart(flayer_id=int(id))

            products = []

            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_sub1category(
                            category=main_catg, sub1category=catg), reverse=True):
                if id not in products:
                    products.append(id)

            sliced = products[0:3]
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            divider = len(products) / 3
            max_pages = math.ceil(divider)
            if max_pages > 1:
                back_page = KeyboardButton(text=f"...")
                pages = KeyboardButton(text=f"1/{max_pages}")
                next = KeyboardButton(text=f"»»»")
                row = [back_page, pages, next]
                markup.row(*row)

            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            for item_id in sliced:

                select = await db.select_product(id=item_id)
                name = select.get("name")
                photos = select.get("photos")

                caption = f"<b>{name}</b>"
                product_cart = f"Удалить из Базы Данных {name}"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)

                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                markup.add(KeyboardButton(text=product_cart))

            await message.answer(f"Вы удалили из Базы Данных <b>{del_name}</b>", reply_markup=markup)
            await Del_Flayer.Lift.set()
            await state.update_data(main_catg=main_catg)
            await state.update_data(catg=catg)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=3)
            await state.update_data(page=1)

        except:
            pass


def register_delete_flat(dp: Dispatcher):
    dp.register_message_handler(del_flayer, IsAdmin(), text="Удалить")
    dp.register_message_handler(select_in_categ, IsAdmin(), state=Del_Flayer.Categ, text=["💼 Портфолио", "Другое", "📝 Заказать", "Назад"])
    dp.register_message_handler(get_order_sub1category, state=Del_Flayer.Sub1)
    dp.register_message_handler(lift_catg_next_order, text=["Назад", "Ortga", "»»»"], state=Del_Flayer.Lift)
    dp.register_message_handler(lift_catg_back_order, text="«««", state=Del_Flayer.Lift)
    dp.register_message_handler(add_cart, state=Del_Flayer.Lift)
