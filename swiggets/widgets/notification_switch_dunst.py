import asyncio

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.switch import Switch
from ..misc import Icons, Substitute


class NotificationSwitchDunst(Switch):
    @validate_call(config=dict(validate_default=True))
    def __init__(self, *,
                 interval=100,
                 icon: Substitute = {
                     True: Icons.bell,
                     False: Icons.bell_slash,
                 },
                 **kwargs):
        super().__init__(interval=interval,
                         **kwargs)
        self.icon = icon
        self.status_cmd = ['dunstctl', 'is-paused']
        self.enable_cmd = ['dunstctl', 'set-paused', 'false']
        self.disable_cmd = ['dunstctl', 'set-paused', 'true']
        self.block = self.add_block(name=type(self).__name__)
        self.is_enabled = None

    async def loop(self):
        if b'false' in await self.status():
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
            await asyncio.sleep(.05)
            await self.loop()
