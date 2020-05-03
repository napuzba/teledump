from typing import TextIO

from telethon.tl.custom.message import Message


class Filter(object):
    def valid(self, msg: Message ) -> bool:
        """ Find whether to include this msg
            :param msg: Raw message object :class:`telethon.tl.types.Message` and derivatives. https://core.telegram.org/type/Message
            :returns: whether to include this msg
        """
        return True
