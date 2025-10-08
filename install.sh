#!/bin/bash

NAME=CopyAsSimLink
SCRIPT=copyassymlink
DESKTOPFILE=plabin-dolphin-copyassymlink.desktop

if [ "$(id -u)" != "0" ]
  then
    echo "This script must be run as root" 1>&2
    exit 1
  else
    echo "Press Enter to install $NAME on your system"
    read
    install -m 644 $DESKTOPFILE "/usr/share/kio/servicemenus/"
    install -m 755 $SCRIPT "/usr/bin/"
    echo "Installation complete. Exit and open Dolphin."
    echo "by @f1r3f0x"
fi