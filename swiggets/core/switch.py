import abc
import asyncio

from .polling import Polling


class Switch(Polling, abc.ABC):
    def __init__(self, interval=600, **kwargs):
        super().__init__(interval=interval,
                         **kwargs)

    async def status(self):
        stat = await asyncio.create_subprocess_exec(
            *self.status_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)
        stdout, _ = await stat.communicate()
        return stdout

    async def enable(self):
        stat = await asyncio.create_subprocess_exec(
            *self.enable_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)
        stdout, _ = await stat.communicate()
        return stdout

    async def disable(self):
        stat = await asyncio.create_subprocess_exec(
            *self.disable_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)
        stdout, _ = await stat.communicate()
        return stdout
