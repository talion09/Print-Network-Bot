from aiogram import types
from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        db = message.bot.get('db')
        admins_list = []
        for id, telegram_id, name in await db.select_all_admins():
            admins_list.append(telegram_id)
        return message.from_user.id in admins_list


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
        )

