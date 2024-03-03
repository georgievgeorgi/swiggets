from psutil import swap_memory
from pydantic import validate_call

from ..core.polling import Polling
from ..misc import Icons, Substitute, block_lower_percent


class SwapMemory(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(
        self,
        format_full=(lambda *,
                     percent_icon, percent, **kw:
                         f'''{Icons.download} {percent_icon} {
                             percent:.1f}%'''),
        format_short=None,
        interval: int = 5,
        percent_icon: Substitute = block_lower_percent,
        threshold: float = 85,
        **kwargs
            ):
        super().__init__(interval=interval)
        self.format_full = format_full
        self.format_short = format_short
        self.percent_icon = percent_icon
        self.threshold = threshold
        self.block = self.add_block(name=type(self).__name__, **kwargs)

    async def loop(self):
        swap = swap_memory()
        res = {'total': swap.total,
               'used': swap.used,
               'free': swap.free,
               'percent': swap.percent,
               'percent_icon': self.percent_icon(swap.percent),
               'sin': swap.sin,
               'sout': swap.sout,
               }
        self.block.full_text = self.format_full(**res)
        if self.format_short is not None:
            self.block.short_text = self.format_short.format(**res)
        if swap.percent > self.threshold:
            self.block.urgent = True
        else:
            self.block.urgent = False
        # self.update()
