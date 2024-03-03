import abc
import asyncio
from typing import List

from .widget import Widget


class StreamingCmd(Widget, abc.ABC):
    def __init__(self,
                 init_cmd: List,
                 streaming_cmd: List,
                 **kwargs):
        super().__init__(**kwargs)
        self.init_cmd = init_cmd
        self.streaming_cmd = streaming_cmd

    @abc.abstractmethod
    async def init_cmd_callback(self, data):
        pass

    @abc.abstractmethod
    async def streaming_cmd_callback(self, data):
        pass

    async def init(self):
        proc = await asyncio.create_subprocess_exec(
                *self.init_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        await self.init_cmd_callback(stdout.decode().strip())

    async def main_loop(self):
        proc = await asyncio.create_subprocess_exec(
                *self.streaming_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        while True:
            stdout = await proc.stdout.readline()
            await self.streaming_cmd_callback(stdout.decode().strip())
