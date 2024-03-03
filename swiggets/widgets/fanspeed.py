import aiofiles

from ..core.polling import Polling
from ..misc import Icons


class FanSpeed(Polling):
    def __init__(self, format_full=Icons.fan+' {speed}',
                 format_short=None,
                 interval: int = 5,
                 **kw_args):
        super().__init__(interval=interval,
                         **kw_args)
        self.format_full = format_full
        self.format_short = format_short
        self.block = self.add_block(name=type(self).__name__)

    async def loop(self):
        async with aiofiles.open('/proc/acpi/ibm/fan', 'r') as f:
            async for line in f:
                if not line.startswith('speed'):
                    continue
                else:
                    speed = line.split()[1]
        self.block.full_text = self.format_full.format(speed=speed)
        # self.update()
