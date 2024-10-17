from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery

from tgbot.handlers.users.portfolio import get_sale_category
from tgbot.handlers.users.start import ru_language, bot_start, admins_list
from tgbot.keyboards.inline.catalog import flayer_clb, booking
from tgbot.states.portfel import Port, Order
from tgbot.states.users import User


async def cart(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    select = await db.select_in_cart(buyer=int(message.from_user.id))
    try:
        select.get("flayer_id")
        cart_text = _("Корзина: \n\n")
        # cart_text = "Корзина: \n\n"
        inline = InlineKeyboardMarkup(row_width=2)
        for id, flayer_id, buyer in await db.select_cart(buyer=int(message.from_user.id)):
            select = await db.select_product(id=flayer_id)
            name = select.get("name")
            name_uz = select.get("name_uz")
            if await ru_language(message):
                cart_text += f"<b>{name}</b>\n\n"
                inline.insert(InlineKeyboardButton(text=f"❌ {name}", callback_data=flayer_clb.new(id=flayer_id)))
            else:
                cart_text += f"<b>{name_uz}</b>\n\n"
                inline.insert(InlineKeyboardButton(text=f"❌ {name_uz}", callback_data=flayer_clb.new(id=flayer_id)))

        count = await db.count_in_cart(buyer=int(message.from_user.id))
        quant = _("Количество")
        # quant = "Количество"
        cart_text += f"\n{quant}: <b>{count}</b>"
        order = _("🗂 Оформить заказ")
        # order = "🗂 Оформить заказ"
        inline.insert(InlineKeyboardButton(text=order, callback_data=booking.new(buyer=message.from_user.id)))

        await message.bot.send_message(message.from_user.id, cart_text, reply_markup=inline)
    except Exception as err:
        print(err)
        await message.bot.send_message(message.from_user.id, "Корзина пустая")


async def delete_prod(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    _ = call.bot.get("lang")

    await call.answer()
    flayer_id = callback_data.get("id")
    await db.delete_flayer_id_cart(buyer=int(call.from_user.id), flayer_id=int(flayer_id))

    cart_text = _("Корзина: \n\n")
    # cart_text = "Корзина: \n\n"
    inline = InlineKeyboardMarkup(row_width=2)
    for id, flayer_id, buyer in await db.select_cart(buyer=int(call.from_user.id)):
        select = await db.select_product(id=flayer_id)
        name = select.get("name")
        name_uz = select.get("name_uz")
        if await ru_language(call):
            cart_text += f"<b>{name}</b>\n\n"
            inline.insert(InlineKeyboardButton(text=f"❌ {name}", callback_data=flayer_clb.new(id=flayer_id)))
        else:
            cart_text += f"<b>{name_uz}</b>\n\n"
            inline.insert(InlineKeyboardButton(text=f"❌ {name_uz}", callback_data=flayer_clb.new(id=flayer_id)))

    count = await db.count_in_cart(buyer=int(call.from_user.id))
    quant = _("Количество")
    # quant = "Количество"
    cart_text += f"\n{quant}: <b>{count}</b>"
    order = _("🗂 Оформить заказ")
    # order = "🗂 Оформить заказ"
    inline.insert(InlineKeyboardButton(text=order, callback_data=booking.new(buyer=call.from_user.id)))

    select = await db.select_in_cart(buyer=int(call.from_user.id))
    try:
        select.get("flayer_id")
        await call.bot.edit_message_text(cart_text, call.from_user.id, call.message.message_id, reply_markup=inline)
    except:
        await call.bot.edit_message_text("Корзина пустая", call.from_user.id, call.message.message_id)


async def booking_call(call: CallbackQuery, callback_data: dict,  state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    await call.answer()
    buyer = callback_data.get("buyer")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    yes = _("Да ✅")
    no = _("Отмена ❌")
    markup.insert(KeyboardButton(text=yes))
    markup.insert(KeyboardButton(text=no))
    send_text = _("Вы уверены, что хотите оформить заказ?")
    await call.bot.send_message(call.from_user.id, "Вы уверены, что хотите оформить заказ?", reply_markup=markup)
    await User.Cart.set()
    await state.update_data(buyer=buyer)


async def booking_mes(message: types.Message,  state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    data = await state.get_data()
    buyer = int(data.get("buyer"))
    yes = _("Да ✅")
    no = _("Отмена ❌")


    if message.text == yes:
        user = await db.select_user(telegram_id=int(buyer))
        brand = user.get("brand")
        name = user.get("name")
        number = user.get("number")

        book = f"<b>Заказ</b>: \n\n" \
               f"Бренд: {brand}\n" \
               f"Телефон: {number} \n" \
               f"Имя: {name} \n\n"
        for id, flayer_id, buyer in await db.select_cart(buyer=int(buyer)):
            select = await db.select_product(id=flayer_id)
            name = select.get("name")
            book += f"<b>{name}</b>\n\n"

        await db.delete_cart(buyer=int(buyer))
        await state.reset_state()
        confirm = _("Ваш заказ успешно принят ✅")
        await message.bot.send_message(153479611, book)
        await message.bot.send_message(message.from_user.id, confirm)
        await bot_start(message, state)
    elif message.text == no:
        await state.reset_state()
        cancel = _("Ваш заказ отменен")
        await message.bot.send_message(message.from_user.id, cancel)
        await bot_start(message, state)
    else:
        pass


def register_cart(dp: Dispatcher):
    dp.register_message_handler(cart, text=["🗑 Корзина", "🗑 Savat"])
    dp.register_callback_query_handler(delete_prod, flayer_clb.filter())
    dp.register_callback_query_handler(booking_call, booking.filter())
    dp.register_message_handler(booking_mes, state=User.Cart)