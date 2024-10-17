import logging

from aiogram import Dispatcher

from tgbot.config import load_config


async def on_startup_notify(dp: Dispatcher):
    config = load_config(".env")
    ADMINS = config.tg_bot.admin_ids
    db = dp.bot.get('db')

    # admins_list = []
    # for id, telegram_id, name in await db.select_all_admins():
    #     admins_list.append(telegram_id)
    try:
        await dp.bot.send_message(ADMINS, "Бот Запущен")
    except Exception as err:
        logging.exception(err)