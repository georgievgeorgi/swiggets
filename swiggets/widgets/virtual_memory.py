from psutil import virtual_memory
from pydantic import validate_call

from ..core.formatter import Formatter
from ..core.polling import Polling
from ..core.substitute import Substitute
from ..misc import Icons, block_lower_percent


class VirtualMemory(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(
        self,
        format_full: Formatter = (
            lambda *, percent_icon, percent, free, **kw:
            f'''{Icons.memory} {percent_icon} {
                percent:.1f}% {free/(1 << 30):.2f}GiB'''),
        format_short: Formatter = None,
        interval: int = 5,
        percent_icon: Substitute = block_lower_percent,
        threshold: float = 85,
        **kwargs
            ):
        super().__init__(interval=interval, **kwargs)
        self.format_full = format_full
        self.format_short = format_short
        self.percent_icon = percent_icon
        self.threshold = threshold
        self.block = self.add_block(name=type(self).__name__, **kwargs)

    async def loop(self):
        mem = virtual_memory()
        res = {'total': mem.total,
               'available': mem.available,
               'percent': mem.percent,
               'percent_icon': self.percent_icon(mem.percent),
               'used': mem.used,
               'free': mem.free,
               'active': mem.active,
               'inactive': mem.inactive,
               'buffers': mem.buffers,
               'cached': mem.cached,
               'shared': mem.shared,
               'slab': mem.slab,
               }
        self.block.full_text = self.format_full(**res)
        self.block.short_text = self.format_short(**res)
        if mem.percent > self.threshold:
            self.block.urgent = True
        else:
            self.block.urgent = False
        # self.update()
