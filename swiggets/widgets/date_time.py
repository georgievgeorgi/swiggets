import time

from ..core.polling import Polling
from ..misc import Icons


class DateTime(Polling):
    def __init__(self, *,
                 format_full=f'{Icons.clock} %F %T %z',
                 format_short=None,
                 interval=1,
                 **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.format_full = format_full
        self.format_short = format_short
        self.block = self.add_block(name=type(self).__name__)

    async def init(self):
        pass

    async def loop(self):
        self.block.full_text = time.strftime(self.format_full)
        if self.format_short is not None:
            self.block.short_text = time.strftime(self.format_short)
        self.update()
