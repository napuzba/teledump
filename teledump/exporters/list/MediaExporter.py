import os.path

from telethon.tl.custom.message import Message
from telethon.tl.types import DocumentAttributeFilename
from telethon.tl.types import MessageMediaDocument

from teledump.exporters.csv.CsvExporterBase import CsvExporterBase
from ..ExporterContext import ExporterContext

from ..csv import TextFilter
from ..csv import NumFilter
from ..csv import Filter


from typing import List

class MediaExporter(CsvExporterBase):
    def __init__(self):
        super().__init__()
        self.filters : List[Filter] = []
        self.init()
        self.values = {}

    def init(self):
        self.col_name     = "name"
        self.col_link     = "link"
        self.col_size     = "size"
        self.col_ext      = "ext"
        self.col_date     = "date"
        self.col_msgId    = "msg-id"
        self.col_chatName = "chat-name"
        self.col_chatId   = "chat-id"


        self._addHeader( self.col_name )
        self._addHeader( self.col_link )
        self._addHeader( self.col_msgId )
        self._addHeader( self.col_size )
        self._addHeader( self.col_ext )
        self._addHeader( self.col_chatName )
        self._addHeader( self.col_chatId )
        self._addHeader( self.col_date)

    def format(self, msg: Message , context: ExporterContext) -> str:
        return self._strRow( self.values )

    def valid(self, msg: Message ) -> bool:
        if not isinstance(msg.media,MessageMediaDocument):
            return False
        self.parse(msg)
        for filter in self.filters:
            if not filter.valid(self.values):
                return False
        return True

    def _addFilter(self,filter ):
        self.filters.append(filter)

    def setConfig(self, value: str):
        super().setConfig(value)
        sColumns = self.config
        for column in sColumns.split(',' ):
            filter = TextFilter.parse(column)
            if filter != None:
                self._addField(filter.key())
                self._addFilter(filter)
                continue
            filter = NumFilter.parse(column)
            if filter != None:
                self._addField(filter.key())
                self._addFilter(filter)
                continue
            self._addField(column)

    def parse(self, msg: Message):
        self.values = {}
        fileName = ext = ""
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeFilename) :
                fileName = attr.file_name
                ext = os.path.splitext(fileName)[1][1:]
        self.values[self.col_name    ] = fileName
        self.values[self.col_link    ] = 'https://t.me/c/{0:d}/{1:d}'.format(msg.chat.id, msg.id)
        self.values[self.col_size    ] = msg.media.document.size // (1024 * 1024)
        self.values[self.col_ext     ] = ext
        self.values[self.col_chatName] = msg.chat.title
        self.values[self.col_chatId  ] = msg.chat.id
        self.values[self.col_msgId   ] = msg.id
        self.values[self.col_date    ] = msg.date.strftime("%Y-%m-%d %H-%M")
