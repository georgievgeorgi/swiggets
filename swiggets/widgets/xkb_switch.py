import asyncio
import re

from pydantic import validate_call

from ..core.streaming_cmd import StreamingCmd
from ..misc import Flags, Substitute


class XKBSwitch(StreamingCmd):
    regex = re.compile(r'(?P<layout>[^(]+)(\((?P<variant>.*)\))?')

    @validate_call(config=dict(validate_default=True))
    def __init__(self, format_full='{flag}', format_short=None,
                 flags: Substitute = {
                     r'us.*': Flags.US,
                     r'bg.*': Flags.BG,
                     r'gr.*': Flags.GR,
                     },
                 **kwargs):
        super().__init__(init_cmd=['xkb-switch'],
                         streaming_cmd=['xkb-switch', '-W'],
                         **kwargs)
        self.format_full = format_full
        self.format_short = format_short
        self.flags = flags
        self.block = self.add_block(name=type(self).__name__)
        self.block.border_top = 0
        self.block.border_bottom = 0
        self.block.markup = 'pango'

    async def click_event(self, evt):
        proc = await asyncio.create_subprocess_exec(
                'xkb-switch', '-n',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        await proc.communicate()

    async def init_cmd_callback(self, data):
        self.apply(data)

    async def streaming_cmd_callback(self, data):
        self.apply(data)

    def apply(self, data):
        vals = self.regex.match(data).groupdict('')
        dct = dict(
            layout=vals['layout'],
            variant=vals['variant'],
            flag=self.flags(data),
            full=data,
        )
        self.block.full_text = self.format_full.format(**dct)
        if self.format_short is not None:
            self.block.short_text = self.format_short.format(**dct)
