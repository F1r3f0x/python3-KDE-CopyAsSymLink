#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
#       PasteAsSymLink
#
#       This script creates a symlink for a given path(s) on the clipboard
#
#       Copyright 2025 Patricio Labin Correa @f1r3f0x <plabin@outlook.cl>
#
import os
import sys
import subprocess
from urllib.parse import urlparse, unquote

def get_clipboard() -> tuple[str, str]:
    """Gets clipboard content from various backends."""
    commands = [
        ['qdbus', 'org.kde.klipper', '/klipper', 'org.kde.klipper.klipper.getClipboardContents'],
        ['wl-paste'],
        ['xclip', '-o', '-selection', 'clipboard'],
        ['xsel', '--clipboard', '--output']
    ]

    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return command[0], result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    print("Error: Could not get clipboard contents. Please make sure you are running KDE Plasma or have xclip, xsel or wl-paste installed.")
    return None

def main() -> None:
    """Creates symbolic links in a target directory based on file paths from the clipboard."""
    # Dolphin passes the file path in the args
    if len(sys.argv) < 2:
        print("Error: No target directory provided.")  # Print statements go to logs.
        sys.exit(1)

    target_directory = sys.argv[1]
    if not os.path.isdir(target_directory):
        print(f"Error: Target directory '{target_directory}' does not exist or is not a directory.")
        sys.exit(1)
        
    command, clipboard_text = get_clipboard()

    if not clipboard_text:
        print("Error: Clipboard is empty or could not be read.")
        sys.exit(1)

    # Clipboard items are separated by newlines
    clipboard_items = ""
    
    if command == "qdbus":
        clipboard_items = clipboard_text.split(' ')
    else:
        clipboard_items = clipboard_text.split('\n')
    
    success_count = 0
    error_count = 0 
    
    # Loop through each line from the clipboard
    for file_path in clipboard_items:
        file_path = file_path.strip()
        if not file_path:  # Skip any empty lines
            continue

        # Parse KDE file paths
        source_path = ""
        if file_path.startswith('file://'):
            parsed_uri = urlparse(file_path)
            source_path = unquote(parsed_uri.path)
        else:
            source_path = file_path

        if not os.path.isabs(source_path):
            print(f"Skipping (not an absolute path): '{source_path}'")
            error_count += 1
            continue

        if not os.path.exists(source_path):
            print(f"Skipping (not found): '{source_path}'")
            error_count += 1
            continue
        
        link_name = os.path.basename(source_path)
        link_path = os.path.join(target_directory, link_name)
        
        try:
            os.symlink(source_path, link_path)
            print(f"Link created: {link_name}")
            success_count += 1
        except FileExistsError:
            print(f"Skipping (already exists): '{link_name}'")
            error_count += 1
        except Exception as e:
            print(f"An unexpected error occurred for '{link_name}': {e}")
            error_count += 1
            
    print(f"\nOperation complete. {success_count} links created, {error_count} items skipped.")

if __name__ == "__main__":
    main()