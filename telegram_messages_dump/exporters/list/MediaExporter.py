import os.path

from telethon.tl.custom.message import Message
from telethon.tl.types import DocumentAttributeFilename
from telethon.tl.types import MessageMediaDocument

from .CsvExporterBase import CsvExporterBase
from ..ExporterContext import ExporterContext

class MediaExporter(CsvExporterBase):
    def __init__(self):
        super().__init__()
        self.key_name = 0
        self.key_id   = 1
        self.key_size = 2
        self.key_ext  = 3
        self._addHeader(self.key_name , "Name")
        self._addHeader(self.key_id   , "ID"  )
        self._addHeader(self.key_size , "Size(MB)")
        self._addHeader(self.key_ext  , "Ext" )

    def format(self, msg: Message , context: ExporterContext) -> str:
        values = {}
        fileName = ext = ""
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeFilename) :
                fileName = attr.file_name
                ext = os.path.splitext(fileName)[1][1:]
        values[self.key_name] = fileName
        values[self.key_id  ] = 'http://t.me/{0:d}/{1:d}'.format(msg.chat.id,msg.id)
        values[self.key_size] = msg.media.document.size // (1024*1024)
        values[self.key_ext]  = ext
        return self._strRow(values)

    def valid(self, msg: Message ) -> bool:
        return isinstance(msg.media,MessageMediaDocument)
