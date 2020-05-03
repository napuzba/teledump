import json
from datetime import date, datetime
from typing import TextIO

from telethon.tl.custom.message import Message

from ..Exporter import Exporter
from ..ExporterContext import ExporterContext
from ..FormatData import FormatData


class JsonlExporter(Exporter):
    """ jsonl exporter plugin.

    As opposed to json exporter jsonl serializes messages as one JSON object per line, not as
    one giant array.

    See http://jsonlines.org.
    """
    # pylint: disable=no-self-use

    def __init__(self):
        """ constructor """
        pass

    # pylint: disable=unused-argument
    def format(self, msg: Message, context: ExporterContext) -> str:
        """ Formatter method. Takes raw msg and converts it to a *one-line* string.
            :param msg: Raw message object :class:`telethon.tl.types.Message` and derivatives.
                        https://core.telegram.org/type/Message

            :returns: *one-line* string containing one message data.
        """
        # pylint: disable=line-too-long
        data = FormatData(msg)

        msgDictionary = {
            'message_id': msg.id,
            'from_id': msg.from_id,
            'reply_id': data.re_id_str,
            'author': data.name,
            'sent_by_bot': data.is_sent_by_bot,
            'date': msg.date,
            'content': data.content,
            'contains_media': data.is_contains_media,
            'media_content': data.media_content
        }
        msg_dump_str = json.dumps(
            msgDictionary, default=self._json_serial, ensure_ascii=False)
        return msg_dump_str

    def begin_final_file(self, output: TextIO, context: ExporterContext) -> None:
        """ Hook executes at the beginning of writing a resulting file.
            (After BOM is written in case of --addbom)
        """
        pass

    def _json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code
           https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))
