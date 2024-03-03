import asyncio
import os
import sys

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.switch import Switch
from ..misc import Icons, Substitute

xrandr_sh = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                         'bin/xrandr-share.sh')


class ScreenShare(Switch):
    @validate_call(config=dict(validate_default=True))
    def __init__(self,
                 icon: Substitute = {
                     True: Icons.users,
                     False: Icons.users_slash,
                 },
                 **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.status_cmd = [xrandr_sh, '--status']
        self.enable_cmd = [xrandr_sh, '--start']
        self.disable_cmd = [xrandr_sh, '--stop']
        self.block = self.add_block(name=type(self).__name__)
        self.is_enabled = None

    async def loop(self):
        if b'true' in await self.status():
            self.is_enabled = True
        else:
            self.is_enabled = False
        self.block.full_text = self.icon(self.is_enabled)
        self.update()

    async def click_event(self, evt):
        if evt.button in {MouseButton.left,
                          MouseButton.middle,
                          MouseButton.right}:
            if self.is_enabled:
                await self.disable()
            else:
                await self.enable()
            await asyncio.sleep(.2)
            await self.loop()
