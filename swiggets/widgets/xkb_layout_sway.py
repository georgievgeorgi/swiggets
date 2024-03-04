import asyncio
import json
import re

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.formatter import Formatter
from ..core.streaming_cmd import StreamingCmd
from ..core.substitute import Substitute
from ..misc import Flags


class XKBLayoutSway(StreamingCmd):
    regex = re.compile(r'(?P<layout>[^(]+)(\((?P<variant>.*)\))?')

    @validate_call(config=dict(validate_default=True))
    def __init__(self,
                 format_full: Formatter = '{flag}',
                 format_short: Formatter = None,
                 flags: Substitute = {
                     r'English.*': Flags.US,
                     r'Bulgarian.*': Flags.BG,
                     r'Greek.*': Flags.GR,
                     },
                 **kwargs):
        super().__init__(init_cmd=['swaymsg', '--type', 'get_inputs', '--raw'],
                         streaming_cmd=['swaymsg', '--type', 'subscribe',
                                        '--monitor', '--raw', '["input"]'],
                         **kwargs)
        self.format_full = format_full
        self.format_short = format_short
        self.flags = flags
        self.block = self.add_block(name=type(self).__name__)
        self.block.border_top = 0
        self.block.border_bottom = 0
        self.block.markup = 'pango'

    async def click_event(self, evt):
        if evt.name is None:
            return
        else:
            if evt.button == MouseButton.wheel_up:
                cmd = ['swaymsg', 'input', 'type:keyboard',
                       'xkb_switch_layout', 'next']
            elif evt.button == MouseButton.wheel_down:
                cmd = ['swaymsg', 'input', 'type:keyboard',
                       'xkb_switch_layout', 'prev']
            elif evt.button == MouseButton.left:
                cmd = ['swaymsg', 'input', 'type:keyboard',
                       'xkb_switch_layout', 'next']
            else:
                return
        proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL)
        await proc.communicate()

    async def init_cmd_callback(self, data):
        for d in json.loads(data):
            self.apply(d)

    async def streaming_cmd_callback(self, data):
        d = json.loads(data)
        if d['change'] == 'xkb_layout':
            self.apply(d['input'])
        self.update()

    def apply(self, data):
        if data['type'] != 'keyboard':
            return
        data = data['xkb_active_layout_name']
        vals = self.regex.match(data).groupdict('')
        dct = dict(
            layout=vals['layout'],
            variant=vals['variant'],
            flag=self.flags(data),
            full=data,
        )
        self.block.full_text = self.format_full(**dct)
        self.block.short_text = self.format_short(**dct)
