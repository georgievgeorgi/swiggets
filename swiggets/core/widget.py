import abc
import asyncio
import logging

from .block import Block

logger = logging.getLogger(__name__)


class Widget(abc.ABC):
    def __init__(self, **kw_block_default):
        self.should_update = True
        self._blocks = []
        self._blocks_name = {}
        self.kw_block_default = kw_block_default
        if 'align' not in self.kw_block_default:
            self.kw_block_default['align'] = 'center'
        if 'min_width' not in self.kw_block_default:
            self.kw_block_default['min_width'] = 10

    @abc.abstractmethod
    async def init(self):
        pass

    @abc.abstractmethod
    async def main_loop(self):
        pass

    async def click_event(self, evt):
        pass

    async def run_forever(self):
        while True:
            try:
                await self.init()
                await self.main_loop()
            except Exception as e:
                logger.exception(repr(e))
            await asyncio.sleep(1)

    def update(self):
        self.should_update = True

    def serialize(self):
        self.should_update = False
        return [b.model_dump(exclude_defaults=True, mode='json')
                for b in self._blocks]

    def json(self):
        self.should_update = False
        return ','.join([b.json(exclude_defaults=True
                                ) for b in self._blocks])

    def sort_blocks(self, key=lambda x: x.name):
        self._blocks = sorted(self._blocks, key=key)

    def add_block(self, where=None, **kw_block):
        kw = dict(self.kw_block_default)
        kw.update(kw_block)
        block = Block(instance=hex(id(self)), **kw)
        block.full_text = ''

        if block.name in self.block_names():
            raise ValueError('name {block.name} already exists')
        if where is None:
            self._blocks.append(block)
        else:
            self._blocks.insert(where, block)
        self._blocks_name[block.name] = block
        return block

    def rm_block_by_name(self, name):
        logger.info(f'{type(self).__name__} rm {name}')
        logger.info(f'{type(self).__name__} {self._blocks_name.keys()}')
        b = self._blocks_name.pop(name)
        self._blocks = [i for i in self._blocks if i is not b]

    def block_names(self):
        return set(self._blocks_name.keys())

    def get_block_by_name(self, name):
        return self._blocks_name[name]
