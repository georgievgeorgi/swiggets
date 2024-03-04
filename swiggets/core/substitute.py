from numbers import Number
from typing import Any, Dict, Pattern, Tuple, Union

from pydantic import RootModel, StrictBool, StrictFloat, StrictInt


class Substitute(RootModel):
    root: Union[str,
                Dict[Union[StrictFloat,
                           StrictInt,
                           StrictBool,
                           Tuple[StrictFloat, StrictFloat],
                           Tuple[StrictInt, StrictInt],
                           Pattern,
                           ],
                     Any]
                ]

    def __call__(self, v):
        if isinstance(self.root, str):
            return self.root
        for cond, subst in self.root.items():
            if isinstance(cond, tuple) and isinstance(v, Number):
                if cond[0] <= v <= cond[1]:
                    return subst
            elif isinstance(cond, Pattern):
                if cond.fullmatch(v):
                    return subst
            elif cond == v:
                return subst
        return v
