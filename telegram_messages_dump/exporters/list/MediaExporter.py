from telethon.tl.custom.message import Message
from telethon.tl.types import MessageMediaDocument

from .CsvExporterBase import CsvExporterBase
from ..ExporterContext import ExporterContext


class MediaExporter(CsvExporterBase):
    def __init__(self):
        super().__init__()
        self.key_name = 0
        self.key_id   = 1
        self._addHeader(self.key_name , "Name")
        self._addHeader(self.key_id   , "ID"  )

    def format(self, msg: Message, context: ExporterContext) -> str:
        values = {}
        values[self.key_name] = msg.media
        values[self.key_id] = msg.id
        return self._strRow(values)
