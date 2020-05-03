import telethon
from telethon.tl.custom.message import Message

from ..Filter import Filter


class HasMedia(Filter):
    def valid(self, msg: Message ) -> bool:
        return isinstance(msg.media,telethon.tl.types.MessageMediaDocument)

