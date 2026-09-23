#!/bin/bash

NAME=CopyAsSymLink
SCRIPT=copyassymlink
DESKTOPFILE=plabin-dolphin-copyassymlink.desktop

if [ "$(id -u)" != "0" ]
  then
    echo "This script must be run as root" 1>&2
    exit 1
  else
    echo "Press Enter to uninstall the first version of $NAME from your system"
    read -r
    rm -vf "/usr/share/kio/servicemenus/$DESKTOPFILE"
    rm -vf "/usr/bin/$SCRIPT"
    echo "Uninstallation complete"
fi