from typing import TextIO

from teledump.exporters.Exporter import Exporter
from teledump.exporters.ExporterContext import ExporterContext
from teledump import utils


class CsvExporterBase(Exporter):
    def __init__(self):
        """ constructor """
        super().__init__()
        self.fields  = []
        self.headers  = {}

    def begin_final_file(self, output : TextIO, context: ExporterContext) -> None:
        if not context.isContinue:
            output.write( self._strHeader() )
            output.write( '\n')

    def _addHeader(self,key, name : str = "") -> None:
        if name == "":
            name = key
        self.headers[key] = name

    def _addField(self,key : str) -> bool:
        if key in self.headers:
            self.fields.append(key)
            return True
        return False

    def _addHeaderField(self, key, name : str) -> None:
        self._addHeader(key,name)
        self.fields.append(key)


    def _strRow(self, values ) -> str:
        def escape(value):
            ss = utils.escape(str(value))
            if (ss.find(",") != -1):
                ss = '"' + ss + '"'
            return ss
        return ','.join(escape(values[kk]) for kk in self.fields)

    def _strHeader(self):
        return ','.join(self.headers[kk] for kk in self.fields)
