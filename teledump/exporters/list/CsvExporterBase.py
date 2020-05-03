from typing import TextIO

from ..Exporter import Exporter
from ..ExporterContext import ExporterContext
from ... import utils


class CsvExporterBase(Exporter):
    def __init__(self):
        """ constructor """
        self.fields  = []
        self.headers = {}

    def begin_final_file(self, output : TextIO, context: ExporterContext) -> None:
        if not context.isContinue:
            output.write( self._strHeader() )
            output.write( '\n')

    def _addHeader(self, key : int , name : str) -> None:
        self.fields.append(key)
        self.headers[key] = name

    def _strRow(self, values ) -> str:
        def escape(value):
            ss = utils.escape(str(value))
            if (ss.find(",") != -1):
                ss = '"' + ss + '"'
            return ss
        return ','.join(escape(values[kk]) for kk in self.fields)

    def _strHeader(self):
        return ','.join(self.headers[kk] for kk in self.fields)
