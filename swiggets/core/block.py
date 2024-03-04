from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, NonNegativeInt, StrictStr, color


class Color(color.Color):
    def __str__(self):
        cols = self.as_rgb_tuple()
        if len(cols) == 3:
            return '#%02X%02X%02X' % cols
        else:
            return '#%02X%02X%02X%02X' % cols


class Block(BaseModel):
    class Config:
        validate_assignment = True
        extra = 'forbid'
    name: str = Field(..., allow_mutation=False)
    instance: str = Field(..., allow_mutation=False)
    full_text: str = None
    short_text: Optional[str] = None
    color: Optional[Color] = None
    background: Optional[Color] = None
    border: Optional[Color] = None
    border_top: NonNegativeInt = 1
    border_right: NonNegativeInt = 1
    border_bottom: NonNegativeInt = 1
    border_left: NonNegativeInt = 1
    min_width: Union[StrictStr, NonNegativeInt] = 0
    align: Literal['left', 'right', 'center'] = 'left'
    urgent: bool = False
    separator: bool = True
    separator_block_width: NonNegativeInt = 9
    markup: Literal['pango', 'none'] = 'none'
