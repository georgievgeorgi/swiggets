#!/usr/bin/env python3
import asyncio
import logging
import time

import psutil

from swiggets import *

logging.basicConfig(
    level=20,
    filename='/tmp/logger',
    filemode='w',
    format="%(name)s\t%(funcName)s()\t%(levelname)s:\t%(message)s"
)

logger = logging.getLogger(__name__)


dispatcher = Dispatcher()
dispatcher.bulk_append_widgets([
    MPD(host='home-media'),
    ScreenShare(),
    # NotificationSwitchMako(),
    NotificationSwitchDunst(),
    PulseAudioSources(device_icons={
        r'alsa_input.usb.*HD_WEBCAM.*': Icons.video,
        r'.*.monitor': Icons.repeat,
        r'bluez_source.*handsfree_head_unit': Icons.headset,
        r'alsa_input.pci.*analog-stereo': Icons.laptop,
        }),
    PulseAudioSinks(device_icons={
        r'bluez_sink.*a2dp_sink': Icons.headphones,
        r'bluez_sink.*handsfree_head_unit': Icons.headset,
        r'alsa_output.pci.*analog-stereo': Icons.laptop,
        r'alsa_output.pci.*hdmi-stereo': Icons.hdmi,
        }),
    FanSpeed(),
    PollingFunc(func=psutil.sensors_temperatures,
                format_full=lambda res: f'{res["k10temp"][0].current:.1f} ℃',),
    PollingFunc(func=lambda: psutil.cpu_freq(True),
                format_full=lambda res: Icons.microchip + ' ' + ''.join([
                    f'{block_lower_percent((r.current-r.min)/(r.max-r.min)*100)}' for r in res])
                ),
    PollingFunc(func=psutil.getloadavg,
                format_full=lambda res: " ".join(f"{i:.2f}" for i in res)),
    VirtualMemory(separator=False),
    SwapMemory(),
    SensorsBattery(),
    DateTime(time_zones=['Europe/Sofia', 'Europe/Madrid', 'Zulu']),
    # XKBLayoutSway(),
    XKBSwitch(),

    # PollingFile(filename='/proc/loadavg'),
    # PollingExec(command='uptime', format_full=lambda stdout, stderr, return_code : f"{stdout[:stdout.find(',')]}", lazy_updates=False),
    # PollingFunc(func=time.time_ns),
    ])


try:
    asyncio.run(dispatcher.run_forever())
except Exception as e:
    logger.exception(repr(e))
