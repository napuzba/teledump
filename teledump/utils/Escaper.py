import re

class Escaper:
    def __init__(self):
        self.ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
        self.ESCAPE_DICT = {
            '\\': '\\\\',
            '"': '""',
            '\b': '\\b',
            '\f': '\\f',
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
        }
        for i in range(0x20):
            self.ESCAPE_DICT.setdefault(chr(i), '\\u{0:04x}'.format(i))

    def escape( self, ss: str ) -> str :
        """Return a JSON representation of a Python string"""
        if not ss:
            return ""
        def replace(match):
            return self.ESCAPE_DICT[match.group(0)]

        return str(self.ESCAPE.sub(replace, ss))
