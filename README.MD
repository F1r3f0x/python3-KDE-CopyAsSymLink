# KDE Dolphin Submenu - Paste as Symbolic Link

## Description:
This will give you a new "Paste as Symbolic Link" submenu on Dolphin. You can create symlinks from files and folders.

## Instructions:
- run `make install`
- quit and reopen Dolphin.
- (optional) run `make dist` to generate the release zip archive.
- (optional) run `make uninstall` to remove the files.

Copy files or folders, then open the destination folder in Dolphin and choose
"Paste as Symbolic Link" from its context menu. Existing destination items are
skipped, and links cannot be created in the same folder as the source items.

## Remove old version:
- run `make uninstall-old` to remove the old `CopyAsSymLink` script.

## Requirements

This script is designed to be compatible with various Linux desktop environments and display servers.

- **Python 3.10 or newer**

- **Clipboard Utilities:**
  The script automatically detects and uses one of the following clipboard tools. At least one must be installed for the script to function.

  | Clipboard Tool    | Test Environment | Working |
  | :- | :- | :- |
  | `qdbus` (Klipper) | KDE Plasma 6 Wayland - CachyOS | ✅ |
  | `wl-paste`        | GNOME Wayland (tested only the script) - Ubuntu 25.04 | ✅ |
  | `xclip`           | Cinnamon X11 - Linux Mint 22.2 (tested only the script) | ✅ |
  | `xsel`            | Cinnamon X11 - Linux Mint 22.2 (tested only the script) | ✅ |

  Available tools are tried in this order: `qdbus`, `wl-paste`, `xclip`, then
  `xsel`. If a tool fails, times out, or returns empty content, the script tries
  the next available option. If none are installed, it exits with a missing
  clipboard dependencies message listing the supported tools.

- **Desktop notifications (optional):** Install `notify-send` or `kdialog` to
  receive success and error notifications. Set `PASTEASSYMLINK_NO_NOTIFY=1` to
  disable notifications.

## Development and tests

Run the unit tests from the repository directory:

```sh
make test
```

The tests use Python's standard-library `unittest` module and mock clipboard
tool availability and subprocess calls, so no clipboard tools or active desktop
session are required. They cover clipboard parsing, backend selection and
fallback, missing dependencies, symlink creation, notifications, and the command
entry point.

To measure test coverage, install the Python `coverage` package and run:

```sh
make coverage
```

## Credit to:
- https://github.com/Faster3ck/MakeDesktopShortcuts for the install and uninstall scripts.
- https://www.opencode.net/williamblair/kde-menu-enhancements bash symlink creation script.
- https://github.com/fabiomux for the make file and archive format.

@f1r3f0x - 2025
