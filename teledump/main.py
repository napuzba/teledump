"""
Usage:

Normal mode:
  telegram-messages-dump -c <chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl] [...]
  telegram-messages-dump --chat=<chat_name> --phone=<phone_num> [--limit=<count>] [--out <file>]

Continuous mode:
  telegram-messages-dump --continue -p <phone_num> -o <file> [-cl] [...]
  telegram-messages-dump --continue=<MSG_ID> -p <phone_num> -o <file> -e <exporter> -c <chat_name>

Where:
    -c,  --chat      Unique name of a channel/chat. E.g. @python.
    -p,  --phone     Phone number. E.g. +380503211234.
    -o,  --out       Output file name or full path. (Default: telegram_<chatName>.log)
    -e,  --exp       Exporter name. text | jsonl | csv (Default: 'text')
      ,  --continue  Continue previous dump. Supports optional integer param <message_id>.
    -l,  --limit     Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -cl, --clean     Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -v,  --verbose   Verbose mode. (Default: False)
      ,  --addbom    Add BOM to the beginning of the output file. (Default: False)
    -h,  --help      Show this help message and exit.
"""
import os
import sys
import logging
from .TelegramDumper import TelegramDumper
from .settings import ChatDumpSettings
from .settings import ChatDumpMetaFile
from .exceptions import MetaFileError
from . import exporters
from . import filters

class Main:
    def __init__(self):
        self.settings : ChatDumpSettings
        self.exporter: exporters.Exporter
        self.filter : filters.Filter
        self.metadata : ChatDumpMetaFile

    def main(self):
        self.loadSettings()
        self.loadLogger()
        self.loadMetaData()
        self.loadExporter()
        self.loadFilter()

        dumper = TelegramDumper(
            os.path.basename(__file__),
            self.settings, self.metadata,
            self.exporter,
            self.filter
        )
        rc = dumper.run()
        sys.exit(rc)

    def loadLogger(self):
        default_format = '%(levelname)s:%(message)s'
        level = logging.INFO
        if self.settings.isVerbose:
            level = logging.DEBUG
        logging.basicConfig(format=default_format, level=level)

    def loadMetaData(self):
        self.metadata = ChatDumpMetaFile(self.settings.outFile)
        # when user specified --continue
        try:
            if self.settings.isIncremental and self.settings.idLastMessage == -1:
                self.metadata.merge(self.settings)
        except MetaFileError as ex:
            print("ERROR: {}".format(ex))
            sys.exit(1)

    def loadExporter(self):
        self.exporter = exporters.load(self.settings.exporter)
        self.exporter.setConfig(self.settings.exporterData)

    def loadFilter(self):
        self.filter = filters.load(self.settings.filter, self.exporter)

    def loadSettings(self):
        self.settings = ChatDumpSettings(__doc__)


Main().main()
