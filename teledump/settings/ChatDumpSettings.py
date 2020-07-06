""" This Module contains classes related to CLI interactions"""

from typing import *

from ..utils import JOIN_CHAT_PREFIX_URL
from .CustomArgumentParser import CustomArgumentParser
from .CustomFormatter import CustomFormatter
from .. import exporters
from .. import filters



class ChatDumpSettings:
    """ Parses CLI arguments. """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, usage):

        # From telegram-cli
        self.api_id = 2899
        self.api_hash = '36722c72256a24c1225de00eb6a1ca74'

        self.chatName     : str  = ""
        self.phoneNum     : str  = ""
        self.outFile      : str  = ""
        self.exporter     : str  = ""
        self.exporterData : str = ""
        self.filter       : str  = ""
        self.limit        : int  = 0
        self.isClean      : bool = False
        self.isVerbose    : bool = False
        self.isAddbom     : bool = False
        self.isQuiet      : bool = False
        self.isIncremental: bool = False
        self.idLastMessage: int = -1


        # Parse parameters
        parser = CustomArgumentParser(formatter_class=CustomFormatter, usage=usage)

        parser.add_argument('-c' , '--chat'    , type=str , default='' )
        parser.add_argument('-p' , '--phone'   , type=str , required=True)
        parser.add_argument('-o' , '--out'     , type=str , default='')
        parser.add_argument('-e' , '--exporter', type=str , default='')
        parser.add_argument(       '--expdata' , type=str, default='')
        parser.add_argument('-f' , '--filter'  , type=str , default='')
        parser.add_argument(       '--continue', type=str , default='*', nargs='?', dest='increment')
        parser.add_argument('-l' , '--limit'   , type=int , default=-1)
        parser.add_argument('-cl', '--clean'   , action='store_true')
        parser.add_argument('-v' , '--verbose' , action='store_true')
        parser.add_argument(       '--addbom'  , action='store_true')
        parser.add_argument('-q' , '--quiet'   , action='store_true')

        args = parser.parse_args()

        # Trim extra spaces in string param values
        args.chat     = args.chat.strip()
        args.exporter = args.exporter.strip()
        args.filter   = args.filter.strip()
        args.out      = args.out.strip()
        args.phone    = args.phone.strip()

        # Detect Normal/Incremental mode
        self._incremental(args, parser)
        # Check if user specified the right options depending on the mode
        self._consistency(args, parser)

        self._validate_limit(args)
        self._validate_exporter(args, parser)
        self._validate_filter(args, parser)
        self._validate_outFile(args)

        self.chatName  = args.chat
        self.isClean   = args.clean
        self.isVerbose = args.verbose
        self.isAddbom  = args.addbom
        self.isQuiet   = args.quiet

    def _incremental(self, args, parser: CustomArgumentParser):
        """ Arguments parsing related to --continue setting """

        if not args.increment == '*':
            # if user specified --continue with/without a parameter
            self.isIncremental = True
            if args.increment:
                # else-if user specified --continue with one param that is expected to be uint
                # Try parse it as int assuming it is the last message_id
                try:
                    self.idLastMessage = int(args.increment)
                except ValueError:
                    parser.error('Unable to parse MSG_ID in --continue=<MSG_ID>')
        return

    def _consistency(self, args, parser : CustomArgumentParser):
        if self.isIncremental:
            if args.out == "":
                parser.error('To increment an existing dump file. You have to specify it using --out or -o setting.')
            if self.idLastMessage != -1:
                # In case of --continue=<MSG_ID>
                if args.chat == "":
                    parser.error('chat name must be specified explicitely when using --continue=<MSG_ID>')
                if args.exporter == "":
                    parser.error('exporter must be specified explicitely when using --continue=<MSG_ID>')
                if args.limit != -1:
                    parser.error('limit setting is not allowed when using --continue=<MSG_ID>')
            else:
                # In case of --continue
                if args.chat != "":
                    parser.error('chat name must NOT be specified explicitely when using --continue')
                if args.exporter != "":
                    parser.error('exporter must NOT be specified explicitely when using --continue')
                if args.filter != "":
                    parser.error('filter must NOT be specified explicitely when using --continue')
                if args.limit != -1:
                    parser.error('limit setting is not allowed when using --continue')
        else:
            # In case of Normal mode
            if args.chat == "":
                parser.error('the following arguments are required: -c/--chat ')

        try:
            zz = int(args.phone) <= 0
            self.phoneNum = args.phone
        except ValueError:
            parser.error('Phone number is invalid.')

    def _validate_limit(self, args):
        # Validate limit / set default
        self.limit = args.limit
        if not self.isIncremental and self.limit < 0:
            self.limit = 100

    def _validate_exporter(self, args, parser):
        # Validate exporter name / set default
        self.exporter = exporters.fallback(args.exporter)
        if not exporters.exist(self.exporter):
            parser.error('No such exporter : <{}>'.format(args.exporter))
        self.exporterData = args.expdata

    def _validate_filter(self, args, parser):
        if args.filter != '':
            self.filter = args.filter
            if not filters.exist(self.filter):
                parser.error('No such filter : <{}>'.format(args.filter))

    def _validate_outFile(self, args):
        # Default output file if not specified by user
        OUTPUT_FILE_TEMPLATE = 'telegram_{}.log'

        if args.out != '':
            outFile = args.out
        elif args.chat.startswith(JOIN_CHAT_PREFIX_URL):
            outFile = OUTPUT_FILE_TEMPLATE.format(args.chat.rsplit('/', 1)[-1])
        else:
            outFile = OUTPUT_FILE_TEMPLATE.format(args.chat)

        self.outFile = outFile
