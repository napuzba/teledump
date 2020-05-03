from .Escaper import Escaper
JOIN_CHAT_PREFIX_URL = 'https://t.me/joinchat/'
_escaper = Escaper()


def escape( ss: str ) -> str :
    return _escaper.escape(ss)
