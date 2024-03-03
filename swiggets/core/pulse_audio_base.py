from pydantic import validate_call

from ..core.widget import Widget


class PulseAudioBase(Widget):
    @validate_call(config=dict(validate_default=True))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_block = self.add_block(align='center',
                                         min_width=20,
                                         name=f'~~{type(self).__name__}')

    def add_remove_device(self, pa_info):
        pa_names = {i.name for i in pa_info}
        for name in self.block_names() - pa_names - {self.main_block.name}:
            self.rm_block_by_name(name)

        for name in pa_names - self.block_names():
            self.add_block(
                where=-1,
                name=name,
                separator=False,
                separator_block_width=0,
                min_width=10,
                align='center',
            )
