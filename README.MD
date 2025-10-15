# KDE Dolphin Submenu - Paste as Symbolic Link

## Description:
This will give you a new "Paste as Symbolic Link" submenu on Dolphin. You can create symlinks from files and folders.

## Instructions:
- run `make install`
- quit and reopen Dolphin.
- (optional) run `make uninstall` to remove the files.

## Remove old version:
- run `make uninstall-old` to remove the old `CopyAsSimLink` script.

## Requirements

This script is designed to be compatible with various Linux desktop environments and display servers.

- **Python 3**

- **Clipboard Utilities:**
  The script automatically detects and uses one of the following clipboard tools. At least one must be installed for the script to function.

  | Clipboard Tool    | Test Environment | Working |
  | :- | :- | :- |
  | `qdbus` (Klipper) | KDE Plasma 6 Wayland - CachyOS | ✅ |
  | `wl-paste`        | GNOME Wayland (tested only the script) - Ubuntu 25.04 | ✅ |
  | `xclip`           | Cinammon X11 - Linux Mint 22.2 (tested only the script) | ✅ |
  | `xsel`            | Cinammon X11 - Linux Mint 22.2 (tested only the script) | ✅ |

## Credit to:
- https://github.com/Faster3ck/MakeDesktopShortcuts for the install and uninstall scripts.
- https://www.opencode.net/williamblair/kde-menu-enhancements bash symlink creation script.
- https://github.com/fabiomux for the make file and archive format.

@f1r3f0x - 2025