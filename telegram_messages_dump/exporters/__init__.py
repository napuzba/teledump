from typing import *
from .Exporter import Exporter
from .ExporterContext import ExporterContext

from .list.CsvExporter   import CsvExporter
from .list.JsonlExporter import JsonlExporter
from .list.TextExporter  import TextExporter
from .list.MediaExporter import MediaExporter


_exporters : Dict[str,lambda : Exporter ] = {
    'text'  : lambda : TextExporter(),
    'csv'   : lambda : CsvExporter(),
    'jsonl' : lambda : JsonlExporter(),
    'media' : lambda : MediaExporter()
}


def fallback(name: str) -> str:
    return 'text' if name == '' else name


def exist( name : str) -> bool:
    return name in _exporters


def load(name: str) -> Union[Exporter,None]:
    if name in _exporters:
        return _exporters[name]()
    return None
