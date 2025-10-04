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

# How to install on Arch / Artix linux

```bash
cd /tmp
mkdir swiggets
cd swiggets
curl -O 'https://raw.githubusercontent.com/georgievgeorgi/swiggets/refs/heads/master/PKGBUILD'
yaourt --pkgbuild --install
```

Alternatively, if you do not like to use yaourt or similar you can satisfy the depenendencies yourself and prepare the package in install using

```bash
makepkg
sudo pacman -U swiggets-*-any.pkg.tar.zst
```

# How to run
## For i3

Copy the provided examples to your `.config` and modify them

```bash
cp /usr/share/swiggets/swiggets-i3-example.py $HOME/.config/i3/swiggets-i3.py
```

Then add it to your `~/.config/i3/config`

```config
bar {
    i3bar_command i3bar
    status_command python $HOME/.config/i3/swiggets-i3.py
    # ...
}
```

## For sway

Copy the provided examples to your `.config` and modify them

```bash
cp /usr/share/swiggets/swiggets-sway-example.py $HOME/.config/sway/swiggets-sway.py
```

Then add it to your `~/.config/i3/config`

```config
bar {
    swaybar_command swaybar
    status_command python $HOME/.config/sway/swiggets-sway.py
    # ...
}
```



# Handy bindings
Having these keybindings in your `config` file will let you use Alt_R as a Push-to-talk button (PTT)
```
bindsym           Alt_R exec "pacmd set-source-mute @DEFAULT_SOURCE@ 0"
bindsym --release Alt_R exec "pacmd set-source-mute @DEFAULT_SOURCE@ 1"
```
