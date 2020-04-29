from .Exporter import Exporter
from .ExporterContext import ExporterContext

from .list.CsvExporter   import CsvExporter
from .list.JsonlExporter import JsonlExporter
from .list.TextExporter  import TextExporter

def load(name: str ) -> Exporter:
    if name == "csv":
        from .list.CsvExporter import CsvExporter
        return CsvExporter()
    if name == "text":
        return TextExporter()
    if name == "jsonl":
        return JsonlExporter()
    return None
