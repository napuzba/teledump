from . import Filter
from typing import Union
from typing import List

import re

class TextFilter(Filter):
    @staticmethod
    def parse(ss : str) -> Union[Filter,None]:
        ss = ss.strip()
        match = re.match("(\w+)\x20*(@=|#=|\$=)(.*)",ss)
        if match is None:
            return None
        key = match.group(1)
        operator = match.group(2)
        partText = match.group(3)
        texts = [ss.strip().lower() for ss in partText.split('|')]
        return TextFilter(key, operator, texts)

    def __init__(self,key: str, operator: str , texts: List[str]):
        super().__init__(key)
        self.operator = operator
        self.texts = texts
        if self.operator == "$=":
            self.patterns = [re.compile(text) for text in self.texts]

    def valid(self,data: dict):
        item = data[self.key()]
        if not isinstance(item, int):
            item = str(item)

        if self.operator == "$=":
            item = item.lower()
            for pattern in self.patterns:
                if pattern.search(item):
                    return True
            return False

        if self.operator == "@=":
            item = item.lower()
            for text in self.texts:
                if item == text:
                    return True
            return False

        if self.operator == "#=":
            item = item.lower()
            for text in self.texts:
                if item.find(text) != -1:
                    return True
                continue

        return False

    def __str__(self):
        return '"key: {}, operator: {} , values : {}"'.format(
            self.key(),
            self.operator,
            self.values
        )

