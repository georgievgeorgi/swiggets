import aiofiles
from pydantic import validate_call

from ..core.formatter import Formatter
from ..core.polling import Polling
from ..core.substitute import Substitute
from ..misc import Icons
from ..misc import battery_percent
from ..misc import timedelta
import time



class PowerSupplyUevent(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(self, *, filename,
                 interval=5,
                 format_full: Formatter = '{battery_icon} {percentage:.2f}% {status_icon} {time_estimate:%h:%M}',
                 format_short: Formatter = None,
                 lazy_updates=True,
                 parse_lines=lambda lines: [li.strip() for li in lines],
                 status_icon: Substitute = {
                     'Charging': Icons.plug_bolt,
                     'Not charging': Icons.plug_check,
                     'Discharging': Icons.plug_xmark,
                 },
                 battery_icon: Substitute = battery_percent,
                 #warning_criteria=lambda:
                 **kwargs):
        super().__init__(interval=interval, **kwargs)
        self.lazy_updates = lazy_updates
        self.filename = filename
        self.format_full = format_full
        self.format_short = format_short
        self.block = self.add_block(name=type(self).__name__)
        self.parse_lines = parse_lines
        self.status_icon = status_icon
        self.battery_icon = battery_percent
        self.last_call_timestamp = -1
        self.last_percentage = 0
        self.last_time_estimate = 0

    async def loop(self):
        async with aiofiles.open(self.filename) as f:
            lines = await f.readlines()
        tt = dict([li.strip().split('=') for li in lines])


        res = {
                'name': tt['POWER_SUPPLY_NAME'] if 'POWER_SUPPLY_NAME' in tt else None,
                'type': tt['POWER_SUPPLY_TYPE'] if 'POWER_SUPPLY_TYPE' in tt else None,
                'status': tt['POWER_SUPPLY_STATUS'] if 'POWER_SUPPLY_STATUS' in tt else None,
            }

        if 'POWER_SUPPLY_ENERGY_FULL' in tt:
            res['full'] = tt['POWER_SUPPLY_ENERGY_FULL']
        elif 'POWER_SUPPLY_CHARGE_FULL' in tt:
            res['full'] = tt['POWER_SUPPLY_CHARGE_FULL']
        else:
            res['full'] = None,



        if 'POWER_SUPPLY_ENERGY_NOW' in tt:
            res['now'] = tt['POWER_SUPPLY_ENERGY_NOW' ]
        elif 'POWER_SUPPLY_CHARGE_NOW' in tt:
            res['now'] = tt['POWER_SUPPLY_CHARGE_NOW' ]
        else:
            res['now'] = None





        if 'POWER_SUPPLY_CURRENT_NOW' in tt:
            res['current'] = tt['POWER_SUPPLY_CURRENT_NOW']
        elif 'POWER_SUPPLY_ENERGY_NOW' in tt:
            res['current'] = tt['POWER_SUPPLY_ENERGY_NOW' ]
        else:
            res['current'] = None
        res['full'] = float(res['full'])
        res['now'] = float(res['now'])
        res['current'] = float(res['current'])/1e6
        res['percentage'] = res['now']/res['full']*100
        res['status_icon'] = self.status_icon(res['status'])
        res['battery_icon'] = self.battery_icon(res['percentage'])


        cur_ts = time.time()
        cur_pct = res['percentage']

        self.last_time_estimate = cur_pct/ (self.last_percentage-cur_pct) *(self.last_call_timestamp - cur_ts)
        res['time_estimate'] = timedelta(seconds=self.last_time_estimate)
        self.last_percentage = cur_pct
        self.last_call_timestamp = cur_ts





        self.block.full_text = self.format_full(**res)
        self.block.short_text = self.format_short(**res)

        if not self.lazy_updates:
            self.update()
