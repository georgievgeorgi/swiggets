import asyncio
import json
import logging
import signal
import sys
from typing import List

from .click_event import ClickEvent
from .widget import Widget

logger = logging.getLogger(__name__)


def signal_SIGCONT(sig, frame):
    logger.debug('SIGCONT')


def signal_SIGSTOP(sig, frame):
    logger.debug('SIGSTOP')


def sighup(sig, frame):
    logger.debug('SIGHUP')
    print(']\n', flush=True)


signal.signal(signal.SIGCONT, signal_SIGCONT)
signal.signal(signal.SIGHUP, sighup)


class Dispatcher:
    def __init__(self):
        self.widgets = {}

    def append_widget(self, widget: Widget):
        self.widgets[hex(id(widget))] = widget

    def bulk_append_widgets(self, widgets: List[Widget]):
        for w in widgets:
            self.append_widget(w)

    @property
    def should_update(self):
        return any([w.should_update for w in self.widgets.values()])

    async def run_forever(self):
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        w_transport, w_protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout)
        writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
        self._stdin = reader
        self._stdout = writer

        await asyncio.gather(
                self._event_processor(),
                self._updater(),
                *[widget.run_forever() for widget in self.widgets.values()]
        )

    async def _writer(self, json: str):
        logger.debug(json)
        self._stdout.write(json.encode())
        await self._stdout.drain()

    async def _updater(self):
        await self._writer('{"version": 1, "click_events": true}\n')
        await self._writer('[[]\n')
        while True:
            if self.should_update:
                ser = [b for w in self.widgets.values() for b in w.serialize()]
                try:
                    dump = json.dumps(ser,
                                      ensure_ascii=False,
                                      indent=2,
                                      separators=(',', ': '),
                                      )
                except Exception as e:
                    logger.info(str(ser))
                    raise (e)
                await self._writer(',' + dump + '\n')
            else:
                await asyncio.sleep(.1)

    async def _event_processor(self):
        while True:
            try:
                signal = (await self._stdin.readline()
                          ).decode().strip('\n\r, \t')
                if signal == '[':
                    signal = (await self._stdin.readline()
                              ).decode().strip('\n\r, \t')
                event = ClickEvent.parse_raw(signal)
                logger.info(repr(event))
                if event.instance in self.widgets:
                    logger.info(f'''Processing by {
                        self.widgets[event.instance]}''')
                    await self.widgets[event.instance].click_event(event)
                else:
                    logger.warning(f'''Widget instance {event.instance
                                   } not found in {self.widgets}''')
            except Exception as e:
                logger.exception(f'signal={signal}, exeption={repr(e)}')
                raise e
