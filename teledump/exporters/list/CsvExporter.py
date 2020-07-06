from telethon.tl.custom.message import Message

from teledump.exporters.csv.CsvExporterBase import CsvExporterBase
from ..ExporterContext import ExporterContext
from ..FormatData import FormatData


class CsvExporter(CsvExporterBase):
    """ csv (comma separated values) exporter plugin.
        By convention it has to be called exactly the same as its file name.
        (Apart from .py extention)
    """
    def __init__(self):
        super().__init__()
        self.key_id      = 0
        self.key_time    = 1
        self.key_sender  = 2
        self.key_replyId = 3
        self.key_message = 4

        self._addField(self.key_id, "Message-Id")
        self._addField(self.key_time, "Time")
        self._addField(self.key_sender, "Sender-Name")
        self._addField(self.key_replyId, "Reply-Id")
        self._addField(self.key_message, "Message")

    def format(self, msg: Message, context: ExporterContext) -> str:
        data = FormatData(msg)
        values = {}
        values[self.key_id     ] = msg.id
        values[self.key_sender ] = data.name
        values[self.key_replyId] = data.re_id_str
        values[self.key_message] = data.content
        values[self.key_time   ] = msg.date.isoformat()
        return self._strRow(values)


