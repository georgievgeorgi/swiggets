import abc
import asyncio

from .widget import Widget


class Polling(Widget, abc.ABC):
    def __init__(self, *, interval=5, **kwargs):
        super().__init__(**kwargs)
        self.interval = interval

    async def init(self, **kwargs):
        pass

    async def main_loop(self):
        while True:
            await self.loop()
            await asyncio.sleep(self.interval)

    @abc.abstractmethod
    async def loop(self):
        pass
