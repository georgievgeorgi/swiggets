from .icons import Icons
from .substitute import Substitute

block_lower_percent = Substitute({
    (float('-inf'), 15.): Icons.block_lower_1_8,
    (15., 33.): Icons.block_lower_2_8,
    (33., 44.): Icons.block_lower_3_8,
    (44., 55.): Icons.block_lower_4_8,
    (55., 66.): Icons.block_lower_5_8,
    (66., 77.): Icons.block_lower_6_8,
    (77., 88.): Icons.block_lower_7_8,
    (88., float('inf')): Icons.block_full,
})
