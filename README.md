# swiggets -- swaybar / i3bar widgets by GG

Widgets can be composed by multiple blocks and mouse events are supported.
For example the PulseAudioSources widget visualizes each input device as a separate block and default devices can be switched by clicking the corresponding icon.

swiggets is only a library without __main__. The user should have their own main file. Examples are provided


Here is a full list of the implemented widgets:
- DateTime
- FanSpeed
- MPD: mpd client that can supprort volume control, start, stop, seek
- NotificationSwitchDunst
- NotificationSwitchMako
- PollingExec
- PollingFile
- PollingFunc
- PulseAudioSinks
- PulseAudioSources
- ScreenShare: splits super wide screen to a 1024x768 and the rest
- SensorsBattery
- SwapMemory
- TimeTrack
- VirtualMemory
- XKBLayoutSway
- XKBSwitch

Three of the widgets can be used as quick-and-dirty widgets. These are:
- PollingExec
- PollingFile
- PollingFunc

The results of these functions can be formatted with a lambda function in order to produce the desierd output. For example
```python
#!/usr/bin/env python3

import asyncio
from swiggets import *
dispatcher = Dispatcher()
dispatcher.append_widget(PollingExec(command='uptime', format_full=lambda stdout, stderr, return_code : f"{stdout[:stdout.find(',')]}", lazy_updates=False))
asyncio.run(dispatcher.run_forever())
```

# Requirements

On Arch / Artix linux one can install the dependencies as:

```bash
sudo pacman -S python-psutil                \
               python-pydantic-extra-types  \
               python-mpd2                  \
               python-aiofiles              \
               noto-fonts-emoji             \
               python-pulsectl              \
               xkb-switch-i3

yaourt -S aur/python-pulsectl-asyncio
```

# How to download
```bash
mkdir -p ~/git
cd ~/git
git clone https://github.com/georgievgeorgi/swiggets.git
```


# In your i3/config or sway/config
Make sure that in the `bar` section of your `~/.config/i3/config` or `~/.config/sway/config` you provide a path to a main file that uses the library. For example:
```
status_command $HOME/git/swiggets/sway.py
```

# Handy bindings
Having these keybindings in your `config` file will let you use Alt_R as a Push-to-talk button (PTT)
```
bindsym           Alt_R exec "pacmd set-source-mute @DEFAULT_SOURCE@ 0"
bindsym --release Alt_R exec "pacmd set-source-mute @DEFAULT_SOURCE@ 1"
```
