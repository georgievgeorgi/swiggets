import aiofiles
from pydantic import validate_call

from ..core.formatter import Formatter
from ..core.polling import Polling


class PollingFile(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(self, *, filename,
                 interval=5,
                 format_full: Formatter = lambda res: f'{res}',
                 format_short: Formatter = None,
                 lazy_updates=True,
                 **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.lazy_updates = lazy_updates
        self.filename = filename
        self.format_full = format_full
        self.format_short = format_short
        self.block = self.add_block(name=type(self).__name__)

    async def loop(self):
        async with aiofiles.open(self.filename) as f:
            res = await f.read()
        res = res.strip()
        self.block.full_text = self.format_full(res)
        self.block.short_text = self.format_short(res)

        if not self.lazy_updates:
            self.update()
