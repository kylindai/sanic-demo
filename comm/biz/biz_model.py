

class UserInfo:

    def __init__(self, name: str):
        self._name = name

    async def name(self, name=None):
        if name is not None:
            self._name = name
        return self._name
