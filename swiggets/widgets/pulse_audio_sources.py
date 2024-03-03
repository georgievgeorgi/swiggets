import logging
from typing import Optional

import pulsectl_asyncio
from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.pulse_audio_base import PulseAudioBase
from ..misc import Icons, Substitute

logger = logging.getLogger(__name__)


class PulseAudioSources(PulseAudioBase):
    @validate_call(config=dict(validate_default=True))
    def __init__(self,
                 main_icon: Substitute = {
                     True: Icons.microphone_enabled,
                     False: Icons.microphone_disabled,
                 },
                 device_icons: Substitute = {},
                 device_format_full: str = '{icon} {volume:.0f}% ',
                 device_format_short: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.device_icons = device_icons
        self.main_icon = main_icon
        self.device_format_full = device_format_full
        self.device_format_short = device_format_short

    def process_vals(self, pa_info):
        self.add_remove_device(pa_info)

        has_enabled = False
        for pa_i in pa_info:
            block = self.get_block_by_name(pa_i.name)
            block.full_text = self.device_format_full.format(
                icon=self.device_icons(pa_i.name),
                volume=pa_i.volume.value_flat*100)

            if self.device_format_short is not None:
                block.short_text = self.device_format_short.format(
                    icon=self.device_icons(pa_i.name),
                    volume=pa_i.volume.value_flat*100)

            if pa_i.mute == 0:
                has_enabled = True
                block.urgent = True
            else:
                block.urgent = False
        self.sort_blocks()

        self.main_block.urgent = has_enabled
        self.main_block.full_text = self.main_icon(has_enabled)
        self.update()

    async def click_event(self, evt):
        try:
            if evt.name == self.main_block.name:
                if (evt.button == MouseButton.right
                        or evt.button == MouseButton.middle
                        or evt.button == MouseButton.left):
                    sources = await self.pulse.source_list()
                    for s in sources:
                        await self.pulse.mute(s, mute=True)
            else:
                source = await self.pulse.get_source_by_name(evt.name)
                if evt.button == MouseButton.wheel_up:
                    await self.pulse.volume_change_all_chans(source, .05)
                elif evt.button == MouseButton.wheel_down:
                    await self.pulse.volume_change_all_chans(source, -.05)
                elif evt.button == MouseButton.left:
                    await self.pulse.source_default_set(source)
                elif evt.button == MouseButton.right:
                    await self.pulse.volume_set_all_chans(source, 0)
                else:
                    logger.info(f'button {evt.button} not handled')
        except Exception as e:
            logger.exception(repr(e))

    async def init(self):
        self.pulse = pulsectl_asyncio.PulseAsync(
            f'{type(self).__name__}-{hex(id(self))}')
        await self.pulse.connect()
        self.process_vals(await self.pulse.source_list())

    async def main_loop(self):
        async for event in self.pulse.subscribe_events('source'):
            self.process_vals(await self.pulse.source_list())
