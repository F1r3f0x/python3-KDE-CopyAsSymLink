#!/bin/bash

# PasteAsSymLink install script
# Copyright 2025 Patricio Labin Correa @f1r3f0x <plabin@outlook.cl>

set -e

NAME="PasteAsSymLink"
SCRIPT="pasteassymlink.py"
DESKTOPFILE="plabin-dolphin-pasteassymlink.desktop"
ACTION=${1:-"--install"}  # Default to --install if no args

SYS_DIR_DESKTOP="/usr/share/kio/servicemenus"
SYS_DIR_BIN="/usr/bin"
USR_DIR_DESKTOP="$HOME/.local/share/kio/servicemenus"
USR_DIR_BIN="$HOME/.local/bin"

# Check if root, change install path.
if [ "$EUID" -eq 0 ]; then  # if su
  echo "Running as root. Performing system-wide installation."
  DIR_DESKTOP="$SYS_DIR_DESKTOP"
  DIR_BIN="$SYS_DIR_BIN"
else
  echo "Running as user. Performing local installation."
  DIR_DESKTOP="$USR_DIR_DESKTOP"
  DIR_BIN="$USR_DIR_BIN"
fi

case "$ACTION" in
  --install)
    echo "Installing $NAME..."
    
    # Ensure target directories exist
    mkdir -p "$DIR_DESKTOP"
    mkdir -p "$DIR_BIN"
    
    # Install files with correct permissions
    install -m 744 "$DESKTOPFILE" "$DIR_DESKTOP/"
    install -m 755 "$SCRIPT" "$DIR_BIN/"
    
    echo "Installation complete!"
    echo "You may need to restart Dolphin for the action to appear."
    ;;
    
  --uninstall)
    echo "Uninstalling $NAME..."
    
    # Remove files
    rm -vf "$DIR_DESKTOP/$DESKTOPFILE"
    rm -vf "$DIR_BIN/$SCRIPT"
    
    echo "Uninstallation complete!"
    ;;
    
  *)
    echo "Error: Unknown argument '$ACTION'"
    echo "Usage: $0 [--install | --uninstall]"
    exit 1
    ;;
esac

exit 0