from enum import IntEnum
from typing import List, Literal, Optional

from pydantic import BaseModel, NonNegativeInt


class MouseButton(IntEnum):
    left = 1
    middle = 2
    right = 3
    wheel_up = 4
    wheel_down = 5
    wheel_right = 6
    wheel_left = 7


class ClickEvent(BaseModel):
    name: Optional[str] = None
    instance: Optional[str] = None
    button: MouseButton
    modifiers: Optional[List[Literal['Control', 'Shift', 'Mod1', 'Mod2',
                                     'Mod3', 'Mod4', 'Mod5']]] = None
    event: Optional[int] = None
    x: NonNegativeInt
    y: NonNegativeInt
    relative_x: NonNegativeInt
    relative_y: NonNegativeInt
    output_x: Optional[NonNegativeInt] = None
    output_y: Optional[NonNegativeInt] = None
    width: NonNegativeInt
    height: NonNegativeInt
