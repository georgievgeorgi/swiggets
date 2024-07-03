import datetime
import zoneinfo
from typing import List, Optional

from pydantic import RootModel, model_validator, validate_call

from ..core.click_event import MouseButton
from ..core.formatter import Formatter
from ..core.polling import Polling
from ..misc import Icons


class TZinfo(RootModel):
    class Config:
        arbitrary_types_allowed = True
    root: Optional[datetime.tzinfo]

    @model_validator(mode='before')
    @classmethod
    def tz_val(cls, data):
        if data is None:
            return data
        return zoneinfo.ZoneInfo(data)


class DateTime(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(
            self, *,
            format_full: Formatter = (lambda now, tzinfo:
                                      Icons.clock +
                                      f' {now:%a %F %T %Z} ({tzinfo})'
                                      ),
            format_short: Formatter = Icons.clock + ' {now:%a %F %R %Z}',
            time_zones: List[TZinfo] = [None, 'Zulu'],
            interval=1,
            **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.format_full = format_full
        self.format_short = format_short
        self.time_zones = time_zones
        self.cur_tz_idx = 0
        self.block = self.add_block(name=type(self).__name__)

    async def init(self):
        pass

    async def loop(self):
        dct = {'now': datetime.datetime.now().astimezone(
            self.time_zones[self.cur_tz_idx].root)}
        dct['tzinfo'] = dct['now'].tzinfo
        self.block.full_text = self.format_full(**dct)
        self.block.short_text = self.format_short(**dct)
        self.block.urgent = self.cur_tz_idx != 0
        self.update()

    async def click_event(self, evt):
        if evt.button == MouseButton.wheel_up:
            self.cur_tz_idx += 1
        elif evt.button == MouseButton.wheel_down:
            self.cur_tz_idx -= 1
        else:
            self.cur_tz_idx = 0
        self.cur_tz_idx = self.cur_tz_idx % len(self.time_zones)
        await self.loop()
