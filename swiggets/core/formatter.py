from typing import Any, Callable, Union

from pydantic import RootModel


class Formatter(RootModel):
    root: Union[None, str, Callable[[Any], str]]

    def __call__(self, *args, **kwargs):
        if self.root is None:
            return None
        elif isinstance(self.root, str):
            return self.root.format(*args, **kwargs)
        else:
            return self.root(*args, **kwargs)
