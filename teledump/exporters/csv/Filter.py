class Filter:
    def __init__(self,key: str):
        self._key : str= key

    def valid(self,data: dict):
        return False

    def key(self) -> str:
        return self._key
