import asyncio

from pydantic import validate_call

from ..core.formatter import Formatter
from ..core.polling import Polling


class PollingExec(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(self, *, command,
                 format_full: Formatter = lambda stdout, stderr, return_code:
                     f'{stdout} ({stderr}) ({return_code})',
                 format_short: Formatter = None,
                 interval=5,
                 lazy_updates=True,
                 **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.lazy_updates = lazy_updates
        self.format_full = format_full
        self.format_short = format_short
        self.command = command
        self.block = self.add_block(name=type(self).__name__)

    async def loop(self):
        proc = await asyncio.create_subprocess_exec(
                *self.command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        dct = {'stdout': stdout.decode().strip(),
               'stderr': stderr.decode().strip(),
               'return_code': proc.returncode,
               }
        self.block.full_text = self.format_full(**dct)
        self.block.short_text = self.format_short(**dct)

        if not self.lazy_updates:
            self.update()
