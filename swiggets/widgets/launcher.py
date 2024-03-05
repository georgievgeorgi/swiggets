import os
import subprocess

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.formatter import Formatter
from ..core.widget import Widget


class Launcher(Widget):
    @validate_call(config=dict(validate_default=True))
    def __init__(self,
                 format: Formatter,
                 command: str,
                 **kwargs):
        super().__init__(**kwargs)
        self.block = self.add_block(name=type(self).__name__)
        self.block.full_text = format()
        self.command = command

    async def init(self):
        pass

    async def main_loop(self):
        pass

    async def run_forever(self):
        pass

    async def click_event(self, evt):
        if evt.button == MouseButton.left:
            subprocess.Popen(self.command, shell=True, preexec_fn=os.setsid)
