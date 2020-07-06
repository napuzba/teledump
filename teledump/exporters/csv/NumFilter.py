from . import Filter
from typing import Union
from typing import List
import re


class NumFilter(Filter):
    @staticmethod
    def parse(ss : str) -> Union[Filter,None]:
        ss = ss.strip()
        match = re.match("(\w+)\x20*(==|<>|>|>=|<|<=)\x20*(\d+)",ss)
        if match is None:
            return None
        key = match.group(1)
        operator = match.group(2)
        num = int(match.group(3))

        return NumFilter(key, operator, num)

    def __init__(self,key: str, operator: str , num: int):
        super().__init__(key)
        self.operator = operator
        self.num = num

    def valid(self,data: dict):
        item = data[self.key()]
        if not isinstance(item, int):
            return False
        if self.operator == "==":
            return item == self.num
        if self.operator == "<>":
            return item != self.num
        if self.operator == ">":
            return item > self.num
        if self.operator == ">=":
            return item >= self.num
        if self.operator == "<":
            return item < self.num
        if self.operator == "<=":
            return item <= self.num
        return False

    def __str__(self):
        return '"key: {}, operator: {} , values : {}"'.format(
            self.key(),
            self.operator,
            self.num
        )

