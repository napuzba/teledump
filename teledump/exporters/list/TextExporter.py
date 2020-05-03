#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import re
from typing import TextIO

from telethon.tl.custom.message import Message

from ..Exporter import Exporter
from ..ExporterContext import ExporterContext
from ..FormatData import FormatData


class TextExporter(Exporter):
    """ text exporter plugin.
        By convention it has to be called exactly the same as its file name.
        (Apart from .py extention)
    """

    def __init__(self):
        """ constructor """
        self.ESCAPE = re.compile(r'[\x00-\x1f\b\f\n\r\t]')
        self.ESCAPE_DICT = {
            '\\': '\\\\',
            # '"': '\\"',
            '\b': '\\b',
            '\f': '\\f',
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
        }
        for i in range(0x20):
            self.ESCAPE_DICT.setdefault(chr(i), '\\u{0:04x}'.format(i))

    def format(self, msg: Message, context: ExporterContext) -> str:
        """ Formatter method. Takes raw msg and converts it to a *one-line* string.
            :param msg: Raw message object :class:`telethon.tl.types.Message` and derivatives.
                        https://core.telegram.org/type/Message

            :returns: *one-line* string containing one message data.
        """
        # pylint: disable=unused-argument
        data = FormatData(msg)

        # Format a message log record
        msg_dump_str = '[{}-{:02d}-{:02d} {:02d}:{:02d}] ID={} {}{}: {}'.format(
            msg.date.year,
            msg.date.month,
            msg.date.day,
            msg.date.hour,
            msg.date.minute,
            msg.id,
            "RE_ID=%s " % data.re_id_str if data.re_id_str else "",
            data.name,
            self._py_encode_basestring(data.content)
        )

        return msg_dump_str

    def begin_final_file(self, output: TextIO, context: ExporterContext) -> None:
        """ Hook executes at the beginning of writing a resulting file.
            (After BOM is written in case of --addbom)
        """
        pass

    # This code is inspired by Python's json encoder's code
    def _py_encode_basestring(self, s):
        """Return a JSON representation of a Python string"""
        if not s:
            return s
        def replace(match):
            return self.ESCAPE_DICT[match.group(0)]
        return self.ESCAPE.sub(replace, s)
