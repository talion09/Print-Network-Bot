import math

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery

from tgbot.handlers.users.start import ru_language, bot_start, admins_list
from tgbot.states.portfel import Port


async def get_sale_category(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    main = _("Главное Меню")
    back = _("Назад")
    markup.insert(KeyboardButton(text=main))
    markup.insert(KeyboardButton(text=back))

    sub1categories = []
    uz_sub1categories = []
    if await ru_language(message):
        for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(await db.select_in_category(
                category="💼 Портфолио")):
            if sub1category not in sub1categories:
                sub1categories.append(sub1category)
                markup.add(KeyboardButton(text=sub1category))
    else:
        for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(await db.select_in_category(
                category="💼 Портфолио")):
            if sub1category_uz not in uz_sub1categories:
                uz_sub1categories.append(sub1category_uz)
                markup.add(KeyboardButton(text=sub1category_uz))
    send_text = _("Выберите категорию")
    await message.answer(send_text, reply_markup=markup)
    await Port.Sub1.set()


# Port.Sub1
async def get_sale_sub1category(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    main = _("Главное Меню")
    back = _("Назад")

    if message.text == back:
        await state.reset_state()
        await bot_start(message, state)
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

            for id, category, sub1category, sub1category_uz, photos, name, name_uz in sorted(await db.select_in_sub1category(category="💼 Портфолио", sub1category=sub1), reverse=True):
                if id not in products:
                    products.append(id)

            sliced = products[0:3]
            for item_id in sliced:
                select = await db.select_product(id=item_id)
                name = select.get("name")
                name_uz = select.get("name_uz")
                photos = select.get("photos")

                if await ru_language(message):
                    caption = f"<b>{name}</b>"
                else:
                    caption = f"<b>{name_uz}</b>"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)
                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)

            divider = len(products) / 3
            max_pages = math.ceil(divider)
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            print("aegag")
            if max_pages > 1:
                back_page = KeyboardButton(text=f"...")
                pages = KeyboardButton(text=f"1/{max_pages}")
                next = KeyboardButton(text=f"»»»")
                row = [back_page, pages, next]
                markup.row(*row)

            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            await message.answer(f"{send_text} <b>{message.text}</b>", reply_markup=markup)
            await Port.Lift.set()
            await state.update_data(main_catg="💼 Портфолио")
            await state.update_data(catg=sub1)
            await state.update_data(sub=message.text)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=3)
            await state.update_data(page=1)
        except:
            pass


# Port.Lift
async def lift_catg_next(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    print("port lift")

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

    if message.text == back:
        await state.reset_state()
        await get_sale_category(message)

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
            for item_id in sliced:
                select = await db.select_product(id=item_id)
                name = select.get("name")
                name_uz = select.get("name_uz")
                photos = select.get("photos")

                if await ru_language(message):
                    caption = f"<b>{name}</b>"
                else:
                    caption = f"<b>{name_uz}</b>"

                media = types.MediaGroup()
                photos_id = photos.split(",")
                last = photos_id[-1]
                photos_id.remove(last)
                for i in photos_id:
                    media.attach(types.InputMediaPhoto(i))
                media.attach(types.InputMediaPhoto(last, caption))
                await message.bot.send_media_group(chat_id=message.from_user.id, media=media)

            pages = KeyboardButton(text=f"{int(page) + 1}/{max_pages}")
            row = [back_page, pages, next]

            markup.row(*row)
            markup.insert(KeyboardButton(text=main))
            markup.insert(KeyboardButton(text=back))
            await message.answer(f"{send_text} <b>{sub}</b>", reply_markup=markup)
            await Port.Lift.set()
            await state.update_data(main_catg=main_catg)
            await state.update_data(catg=catg)
            await state.update_data(sub=sub)
            await state.update_data(max_pages=max_pages)
            await state.update_data(quant=quant_plus)
            await state.update_data(page=int(page) + 1)


# Port.Lift
async def lift_catg_back(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    print("port lift back")


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
        for item_id in sliced:
            select = await db.select_product(id=item_id)
            name = select.get("name")
            name_uz = select.get("name_uz")
            photos = select.get("photos")

            if await ru_language(message):
                caption = f"<b>{name}</b>"
            else:
                caption = f"<b>{name_uz}</b>"

            media = types.MediaGroup()
            photos_id = photos.split(",")
            last = photos_id[-1]
            photos_id.remove(last)
            for i in photos_id:
                media.attach(types.InputMediaPhoto(i))
            media.attach(types.InputMediaPhoto(last, caption))
            await message.bot.send_media_group(chat_id=message.from_user.id, media=media)

        pages = KeyboardButton(text=f"{int(page) - 1}/{max_pages}")
        row = [back_page, pages, next]

        markup.row(*row)
        markup.insert(KeyboardButton(text=main))
        markup.insert(KeyboardButton(text=back))
        await message.answer(f"{send_text} <b>{sub}</b>", reply_markup=markup)
        await Port.Lift.set()
        await state.update_data(main_catg=main_catg)
        await state.update_data(catg=catg)
        await state.update_data(sub=sub)
        await state.update_data(max_pages=max_pages)
        await state.update_data(quant=quant_new)
        await state.update_data(page=int(page) - 1)


def register_portfolio(dp: Dispatcher):
    dp.register_message_handler(get_sale_category, text=["💼 Портфолио", "💼 Portfolio"])
    dp.register_message_handler(get_sale_sub1category, state=Port.Sub1)
    dp.register_message_handler(lift_catg_next, text=["Назад", "Ortga", "»»»"], state=Port.Lift)
    dp.register_message_handler(lift_catg_back, text="«««", state=Port.Lift)


