import asyncio
import logging

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.switch import Switch
from ..misc import Icons, Substitute

logger = logging.getLogger(__name__)


class NotificationSwitchMako(Switch):
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
        self.status_cmd = ['makoctl', 'mode']
        self.enable_cmd = ['makoctl', 'mode', '-r', 'do-not-disturb']
        self.disable_cmd = ['makoctl', 'mode', '-a', 'do-not-disturb']
        self.block = self.add_block(name=type(self).__name__)
        self.is_enabled = None

    async def loop(self):
        if b'do-not-disturb' in await self.status():
            self.is_enabled = False
        else:
            self.is_enabled = True
        self.block.full_text = self.icon(self.is_enabled)
        self.update()

    async def click_event(self, evt):
        if evt.button in {MouseButton.left,
                          MouseButton.middle,
                          MouseButton.right}:
            if self.is_enabled:
                await self.disable()
                logger.exception('was enabled. DISABLE')
            else:
                await self.enable()
            await asyncio.sleep(.05)
            await self.loop()
