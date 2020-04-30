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
from .exporters import *

def main():
    """ Entry point. """
    settings = ChatDumpSettings(__doc__)

    # define the console output verbosity
    default_format = '%(levelname)s:%(message)s'
    if settings.is_verbose:
        logging.basicConfig(format=default_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=default_format, level=logging.INFO)

    metadata : ChatDumpMetaFile = ChatDumpMetaFile(settings.out_file)

    # when user specified --continue
    try:
        if settings.is_incremental_mode and settings.last_message_id == -1:
            metadata.merge(settings)
    except MetaFileError as ex:
        sprint("ERROR: %s" % ex)
        sys.exit(1)

    exporter : Exporter = load(settings.exporter)
    if ( not exporter ) :
        print("ERROR: No such exporter <{}>".format(settings.exporter) )
        sys.exit(1)

    sys.exit(TelegramDumper(os.path.basename(__file__), settings, metadata, exporter).run())


