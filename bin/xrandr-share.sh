#!/bin/bash

SHARE=ShareMonitor
MAIN_MONITOR=MainMonitor


case $1 in
  --start)
    x=$((3440-1024));y=1440; xrandr --setmonitor $MAIN_MONITOR ${x}/$((x/4))x${y}/$((y/4))+1024+0 DisplayPort-0
    x=1024;y=768; xrandr --setmonitor $SHARE ${x}/$((x/4))x${y}/$((y/4))+0+200 none
    ;;
  --stop)
    xrandr --delmonitor $SHARE
    xrandr --delmonitor $MAIN_MONITOR
    ;;
  --toggle)
    $0 --status && $0 --stop || $0 --start
    ;;
  --status)
    xrandr --listmonitors | grep -q $SHARE && echo true || echo false
    ;;
  *)
    echo $0 --start/--stop/--status/--toggle
esac
