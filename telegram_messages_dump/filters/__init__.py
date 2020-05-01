from typing import *
from .Filter import Filter
from .list.HasMedia import HasMedia

from .list.All import All
from .list.HasMedia import HasMedia


_filters : Dict[str,lambda : Filter ]= {
    'all'       : lambda : All(),
    'has-media' : lambda : HasMedia(),
}


def fallback(name: str) -> str:
    return 'all' if name == '' else name


def exist( name : str) -> bool:
    return name in _filters


def load(name: str) -> Union[Filter,None]:
    if name in _filters:
        return _filters[name]()
    return None
