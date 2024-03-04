from psutil import sensors_battery
from pydantic import validate_call

from ..core.formatter import Formatter
from ..core.polling import Polling
from ..misc import Icons, Substitute, battery_percent


class SensorsBattery(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(
        self,
        format_full: Formatter = '{battery_icon} {percent:.2f}% {mins_left:.1f}min {plug_icon}',  # noqa: E501
        format_short: Formatter = None,
        interval: int = 5,
        battery_icon: Substitute = battery_percent,
        plug_icon: Substitute = {
            False: f"<span fgcolor='#EE8899'>{Icons.plug_xmark}</span>",
            True: f"<span fgcolor='#AAEEBB'>{Icons.plug_check}</span>",
            },
        threshold: float = 8,
        **kw_args
            ):
        super().__init__(interval=interval, **kw_args)
        self.format_full = format_full
        self.format_short = format_short
        self.battery_icon = battery_icon
        self.plug_icon = plug_icon
        self.threshold = threshold
        self.block = self.add_block(name=type(self).__name__, markup='pango')

    async def loop(self):
        bat = sensors_battery()
        res = {'plug_icon': self.plug_icon(bat.power_plugged),
               'battery_icon': self.battery_icon(bat.percent),
               'percent': bat.percent,
               'mins_left': bat.secsleft/60,
               }
        self.block.full_text = self.format_full(**res)
        self.block.short_text = self.format_short(**res)
        if bat.percent < self.threshold:
            self.block.urgent = True
        else:
            self.block.urgent = False
        # self.update()
