import math

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery

from tgbot.handlers.users.portfolio import get_sale_category
from tgbot.handlers.users.start import ru_language, bot_start, admins_list
from tgbot.keyboards.inline.catalog import flayer_clb
from tgbot.states.portfel import Port, Order


async def get_order_category(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    main = _("Главное Меню")
    back = _("Назад")
    another = _("Другое")

    markup.insert(KeyboardButton(text=main))
    markup.insert(KeyboardButton(text=back))

    sub1categories = []
    uz_sub1categories = []
    if await ru_language(message):
        for id, category, sub1category, sub1category_uz, photos, name, name_uz,  in sorted(await db.select_in_category(
                category="📝 Заказать")):
            if sub1category not in sub1categories:
                sub1categories.append(sub1category)
                markup.add(KeyboardButton(text=sub1category))
        markup.add(KeyboardButton(text=another))
    else:
        for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(await db.select_in_category(
                category="📝 Заказать")):
            if sub1category_uz not in uz_sub1categories:
                uz_sub1categories.append(sub1category_uz)
                markup.add(KeyboardButton(text=sub1category_uz))
        markup.add(KeyboardButton(text=another))
    send_text = _("Выберите категорию")
    await message.answer(send_text, reply_markup=markup)
    await Order.Sub1.set()


# Order.Sub1
async def get_order_sub1category(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    main = _("Главное Меню")
    back = _("Назад")
    another = _("Другое")

    if message.text == back:
        await state.reset_state()
        await bot_start(message, state)
    elif message.text == another:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.insert(KeyboardButton(text=main))
        markup.insert(KeyboardButton(text=back))
        sub1categories = []
        uz_sub1categories = []
        if await ru_language(message):
            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_category(
                            category="Другое")):
                if sub1category not in sub1categories:
                    sub1categories.append(sub1category)
                    markup.add(KeyboardButton(text=sub1category))
        else:
            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_category(
                            category="Другое")):
                if sub1category_uz not in uz_sub1categories:
                    uz_sub1categories.append(sub1category_uz)
                    markup.add(KeyboardButton(text=sub1category_uz))
        send_text = _("Выберите подкатегорию")
        await message.answer(send_text, reply_markup=markup)
        await Order.Sub2.set()
    else:
        products = []
        send_text = _("Наши продукты в категории")
        await state.update_data(sub1=message.text)

        try:
            if await ru_language(message):
                select = await db.select_product(sub1category=message.text)
            else:
                select = await db.select_product(sub1category_uz=message.text)
            sub1 = select.get("sub1category")

            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_sub1category(
                            category="📝 Заказать", sub1category=sub1), reverse=True):
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
                name_uz = select.get("name_uz")
                photos = select.get("photos")

                if await ru_language(message):
                    caption = f"<b>{name}</b>"
                    product_cart = f"Добавить в Корзину {name}"
                else:
                    caption = f"<b>{name_uz}</b>"
                    product_cart = f"Savatga qo'shish {name_uz}"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)

                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                markup.add(KeyboardButton(text=product_cart))

                # media = types.MediaGroup()
                # photos_id = photos.split(",")
                # add_to_cart = "Добавить в корзину"
                # inline = InlineKeyboardMarkup(row_width=1)
                # inline.insert(InlineKeyboardButton(text=add_to_cart, callback_data=flayer_clb.new(id=item_id)))
                # for i in photos_id:
                #     media.attach(types.InputMediaPhoto(i))
                # await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                # await message.bot.send_message(chat_id=message.from_user.id, text=caption, reply_markup=inline)

            await message.answer(f"{send_text} <b>{message.text}</b>", reply_markup=markup)
            await Order.Lift.set()
            await state.update_data(main_catg="📝 Заказать")
            await state.update_data(catg=sub1)
            await state.update_data(sub=message.text)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=3)
            await state.update_data(page=1)
        except:
            pass


# Order.Sub2
async def get_order_sub2category(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    main = _("Главное Меню")
    back = _("Назад")
    another = _("Другое")

    if message.text == back:
        await state.reset_state()
        await get_order_category(message)
    else:
        products = []
        send_text = _("Наши продукты в подкатегории")
        await state.update_data(sub1=message.text)

        try:
            if await ru_language(message):
                select = await db.select_product(sub1category=message.text)
            else:
                select = await db.select_product(sub1category_uz=message.text)
            sub1 = select.get("sub1category")

            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                    await db.select_in_sub1category(
                            category="Другое", sub1category=sub1), reverse=True):
                if id not in products:
                    products.append(id)

            sliced = products[0:3]
            divider = len(products) / 3
            max_pages = math.ceil(divider)
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
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
                name_uz = select.get("name_uz")
                photos = select.get("photos")

                if await ru_language(message):
                    caption = f"<b>{name}</b>"
                    product_cart = f"Добавить в Корзину {name}"
                else:
                    caption = f"<b>{name_uz}</b>"
                    product_cart = f"Savatga qo'shish {name_uz}"

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
            await Order.Lift.set()
            await state.update_data(main_catg="Другое")
            await state.update_data(catg=sub1)
            await state.update_data(sub=message.text)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=3)
            await state.update_data(page=1)
        except:
            pass


# Order.Lift
async def lift_catg_next_order(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")
    sub = data.get("sub")
    max_pages = data.get("max_pages")
    quant = data.get("quant")
    page = data.get("page")

    main = _("Главное Меню")
    back = _("Назад")
    send_text = _("Наши продукты в категории")

    if message.text == back:
        if main_catg == "📝 Заказать":
            await state.reset_state()
            await get_order_category(message)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            sub1categories = []
            uz_sub1categories = []
            if await ru_language(message):
                for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                        await db.select_in_category(
                            category=main_catg)):
                    if sub1category not in sub1categories:
                        sub1categories.append(sub1category)
                        markup.add(KeyboardButton(text=sub1category))
            else:
                for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(
                        await db.select_in_category(
                            category=main_catg)):
                    if sub1category_uz not in uz_sub1categories:
                        uz_sub1categories.append(sub1category_uz)
                        markup.add(KeyboardButton(text=sub1category_uz))
            send_text = _("Выберите подкатегорию")
            await message.answer(send_text, reply_markup=markup)
            await Order.Sub2.set()
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
                name_uz = select.get("name_uz")
                photos = select.get("photos")

                if await ru_language(message):
                    caption = f"<b>{name}</b>"
                    product_cart = f"Добавить в Корзину {name}"
                else:
                    caption = f"<b>{name_uz}</b>"
                    product_cart = f"Savatga qo'shish {name_uz}"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)
                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
                markup.add(KeyboardButton(text=product_cart))

            await message.answer(f"{send_text} <b>{sub}</b>", reply_markup=markup)
            await Order.Lift.set()
            await state.update_data(main_catg=main_catg)
            await state.update_data(catg=catg)
            await state.update_data(sub=sub)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=quant_plus)
            await state.update_data(page=int(page) + 1)


# Order.Lift
async def lift_catg_back_order(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")
    sub = data.get("sub")
    max_pages = data.get("max_pages")
    quant = data.get("quant")
    page = data.get("page")

    main = _("Главное Меню")
    back = _("Назад")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    send_text = _("Наши продукты в категории")

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
            name_uz = select.get("name_uz")
            photos = select.get("photos")

            if await ru_language(message):
                caption = f"<b>{name}</b>"
                product_cart = f"Добавить в Корзину {name}"
            else:
                caption = f"<b>{name_uz}</b>"
                product_cart = f"Savatga qo'shish {name_uz}"

            media = types.MediaGroup()
            photos_id = photos.split(",")
            last = photos_id[-1]
            photos_id.remove(last)
            for i in photos_id:
                media.attach(types.InputMediaPhoto(i))
            media.attach(types.InputMediaPhoto(last, caption))
            await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
            markup.add(KeyboardButton(text=product_cart))

        await message.answer(f"{send_text} <b>{sub}</b>", reply_markup=markup)
        await Order.Lift.set()
        await state.update_data(main_catg=main_catg)
        await state.update_data(catg=catg)
        await state.update_data(sub=sub)
        await state.update_data(max_pages=max_pages)
        await state.update_data(quant=quant_new)
        await state.update_data(page=int(page) - 1)


# Order.Lift
async def add_cart(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    main_catg = data.get("main_catg")
    catg = data.get("catg")

    if await ru_language(message):
        if "Добавить в Корзину " in message.text:
            name = message.text[19:]
            try:
                select = await db.select_product_in_sub1category(category=main_catg, sub1category=catg, name=name)
                id = select.get("id")
                select_in_c = await db.select_in_cart(buyer=int(message.from_user.id), flayer_id=int(id))
                try:
                    select_in_c.get("flayer_id")
                    await message.answer(f"В Корзине уже есть <b>{name}</b>")
                except:
                    await db.add_to_cart(flayer_id=int(id), buyer=message.from_user.id)
                    await message.answer(f"Вы добавили в Корзину <b>{name}</b>")
            except:
                pass
    else:
        if "Savatga qo'shish " in message.text:
            name_uz = message.text[17:]
            try:
                select = await db.select_product_in_sub1category_uz(category=main_catg, sub1category=catg,
                                                                    name_uz=name_uz)
                id = select.get("id")
                select_in_c = await db.select_in_cart(buyer=int(message.from_user.id), flayer_id=int(id))
                try:
                    select_in_c.get("flayer_id")
                    await message.answer(f"Savatda allaqachon bor <b>{name_uz}</b>")
                except:
                    await db.add_to_cart(flayer_id=int(id), buyer=message.from_user.id)
                    await message.answer(f"Siz savatga qo'shdingiz <b>{name_uz}</b>")

            except:
                pass


def register_order(dp: Dispatcher):
    dp.register_message_handler(get_order_category, text=["📝 Заказать", "📝 Buyurtma berish",
                                                          "Цены товаров", "Цены товаров"])
    dp.register_message_handler(get_order_sub1category, state=Order.Sub1)
    dp.register_message_handler(get_order_sub2category, state=Order.Sub2)
    dp.register_message_handler(lift_catg_next_order, text=["Назад", "Ortga", "»»»"], state=Order.Lift)
    dp.register_message_handler(lift_catg_back_order, text="«««", state=Order.Lift)
    dp.register_message_handler(add_cart, state=Order.Lift)




