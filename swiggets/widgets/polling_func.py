from ..core.polling import Polling


class PollingFunc(Polling):
    def __init__(self, *, func,
                 interval=5,
                 format_full=lambda res: f'{res}',
                 format_short=None,
                 lazy_updates=True,
                 **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.lazy_updates = lazy_updates
        self.format_full = format_full
        self.format_short = format_short
        self.func = func
        self.block = self.add_block(name=type(self).__name__)

    async def loop(self):
        res = self.func()
        self.block.full_text = self.format_full(res)
        if self.format_short is not None:
            self.block.short_text = self.format_short(res)
        if not self.lazy_updates:
            self.update()
