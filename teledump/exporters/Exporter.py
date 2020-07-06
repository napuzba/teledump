from typing import TextIO

from telethon.tl.custom.message import Message

from .ExporterContext import ExporterContext
from ..filters import Filter

class Exporter(Filter):
    def __init__(self):
        self.config : str = ""

    def format(self, msg: Message, context : ExporterContext ) -> str:
        """ Formatter method. Takes raw msg and converts it to a *one-line* string.
            :param msg: Raw message object :class:`telethon.tl.types.Message` and derivatives.
                        https://core.telegram.org/type/Message
            :returns: *one-line* string containing one message data.
        """
        return ""

    def begin_final_file(self, output: TextIO , context: ExporterContext ) -> None:
        """ Hook executes at the beginning of writing a resulting file.
            (After BOM is written in case of --addbom)
        """
        pass

    def setConfig(self, value: str):
         self.config= value
