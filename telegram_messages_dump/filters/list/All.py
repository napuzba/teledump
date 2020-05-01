from telethon.tl.custom.message import Message
from ..Filter import Filter

class All(Filter):
    def valid(self, msg: Message ) -> bool:
        return True
