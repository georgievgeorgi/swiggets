from .icons import Icons
from .substitute import Substitute

battery_percent = Substitute({
    (float('-inf'), 5): Icons.battery_md_0,
    (5, 15): Icons.battery_md_10,
    (15, 25): Icons.battery_md_20,
    (25, 35): Icons.battery_md_30,
    (35, 45): Icons.battery_md_40,
    (45, 55): Icons.battery_md_50,
    (55, 65): Icons.battery_md_60,
    (65, 75): Icons.battery_md_70,
    (75, 85): Icons.battery_md_80,
    (85, 95): Icons.battery_md_90,
    (95, float('inf')): Icons.battery_md_100,
})
