import asyncio

from ..core.polling import Polling


class PollingExec(Polling):
    def __init__(self, *, command,
                 format_full=lambda stdout, stderr, retcode:
                     f'{stdout} ({stderr}) ({retcode})',
                 format_short=None,
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
        self.block.full_text = self.format_full(stdout.decode().strip(),
                                                stderr.decode().strip(),
                                                proc.returncode)

        if self.format_short is not None:
            self.block.short_text = self.format_short(stdout.decode().strip(),
                                                      stderr.decode().strip(),
                                                      proc.returncode)

        if not self.lazy_updates:
            self.update()
