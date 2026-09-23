#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for pasteassymlink.py."""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable desktop notifications during tests
os.environ["PASTEASSYMLINK_NO_NOTIFY"] = "1"

import pasteassymlink


class TestParseClipboardItems(unittest.TestCase):
    """Tests for parse_clipboard_items."""

    def test_space_separated_file_uris(self):
        """Klipper / qdbus format: multiple file:// URIs separated by spaces."""
        text = "file:///home/user/file1.txt file:///home/user/file2.txt"
        expected = ["file:///home/user/file1.txt", "file:///home/user/file2.txt"]
        self.assertEqual(pasteassymlink.parse_clipboard_items(text), expected)

    def test_newline_separated_file_uris(self):
        """Standard text/uri-list: multiple file:// URIs separated by newlines."""
        text = "file:///home/user/file1.txt\nfile:///home/user/file2.txt\n"
        expected = ["file:///home/user/file1.txt", "file:///home/user/file2.txt"]
        self.assertEqual(pasteassymlink.parse_clipboard_items(text), expected)

    def test_crlf_separated_file_uris(self):
        """RFC 2483 format: multiple file:// URIs separated by CRLF."""
        text = "file:///home/user/file1.txt\r\nfile:///home/user/file2.txt\r\n"
        expected = ["file:///home/user/file1.txt", "file:///home/user/file2.txt"]
        self.assertEqual(pasteassymlink.parse_clipboard_items(text), expected)

    def test_raw_paths_with_spaces(self):
        """Plaintext paths on separate lines, containing spaces."""
        text = "/home/user/My Photos/vacation 1.jpg\n/home/user/My Documents/notes.txt"
        expected = [
            "/home/user/My Photos/vacation 1.jpg",
            "/home/user/My Documents/notes.txt",
        ]
        self.assertEqual(pasteassymlink.parse_clipboard_items(text), expected)

    def test_empty_clipboard_text(self):
        """Empty or whitespace clipboard text returns an empty list."""
        self.assertEqual(pasteassymlink.parse_clipboard_items(""), [])
        self.assertEqual(pasteassymlink.parse_clipboard_items("   \n\t  "), [])


class TestParseSourcePath(unittest.TestCase):
    """Tests for parse_source_path."""

    def test_standard_file_uri(self):
        uri = "file:///home/user/Documents/report.pdf"
        self.assertEqual(
            pasteassymlink.parse_source_path(uri), "/home/user/Documents/report.pdf"
        )

    def test_percent_encoded_file_uri(self):
        uri = "file:///home/user/My%20Photos/summer%20trip%202025.jpg"
        self.assertEqual(
            pasteassymlink.parse_source_path(uri),
            "/home/user/My Photos/summer trip 2025.jpg",
        )

    def test_trailing_slash_normalization(self):
        """Issue 1.2: directory URIs with trailing slashes should not produce empty basenames."""
        uri = "file:///home/user/Documents/Projects/"
        normalized = pasteassymlink.parse_source_path(uri)
        self.assertEqual(normalized, "/home/user/Documents/Projects")
        self.assertEqual(os.path.basename(normalized), "Projects")

    def test_plain_absolute_path(self):
        path = "/home/user/Music/song.mp3"
        self.assertEqual(pasteassymlink.parse_source_path(path), path)

    def test_relative_path_rejected(self):
        """Relative paths should be rejected as not absolute."""
        self.assertIsNone(pasteassymlink.parse_source_path("relative/path/to/file.txt"))

    def test_empty_path(self):
        self.assertIsNone(pasteassymlink.parse_source_path(""))
        self.assertIsNone(pasteassymlink.parse_source_path("   "))


class TestCreateSymlinks(unittest.TestCase):
    """Tests for create_symlinks filesystem operations."""

    def setUp(self):
        self.source_dir = tempfile.TemporaryDirectory()
        self.target_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.source_dir.cleanup()
        self.target_dir.cleanup()

    def test_create_symlink_for_file_and_directory(self):
        # Create a sample file and a sample folder in source
        file_path = os.path.join(self.source_dir.name, "example.txt")
        with open(file_path, "w") as f:
            f.write("content")

        dir_path = os.path.join(self.source_dir.name, "example_folder")
        os.makedirs(dir_path)

        items = [f"file://{file_path}", f"file://{dir_path}/"]

        success, errors = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success, 2)
        self.assertEqual(errors, 0)

        # Verify symlinks exist and point to the right targets
        target_file_link = os.path.join(self.target_dir.name, "example.txt")
        target_dir_link = os.path.join(self.target_dir.name, "example_folder")

        self.assertTrue(os.path.islink(target_file_link))
        self.assertTrue(os.path.islink(target_dir_link))
        self.assertEqual(os.path.realpath(target_file_link), os.path.realpath(file_path))
        self.assertEqual(os.path.realpath(target_dir_link), os.path.realpath(dir_path))

    def test_skip_already_existing_symlink(self):
        file_path = os.path.join(self.source_dir.name, "duplicate.txt")
        with open(file_path, "w") as f:
            f.write("test")

        items = [f"file://{file_path}"]

        # First run creates the link
        success1, errors1 = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success1, 1)
        self.assertEqual(errors1, 0)

        # Second run should skip due to FileExistsError
        success2, errors2 = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success2, 0)
        self.assertEqual(errors2, 1)

    def test_skip_nonexistent_source(self):
        non_existent = os.path.join(self.source_dir.name, "ghost.txt")
        items = [f"file://{non_existent}"]

        success, errors = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success, 0)
        self.assertEqual(errors, 1)

    def test_root_path_empty_basename_skipped(self):
        items = ["file:///"]
        success, errors = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success, 0)
        self.assertEqual(errors, 1)

    def test_invalid_source_path_skipped(self):
        items = ["relative/not_an_abs_path.txt"]
        success, errors = pasteassymlink.create_symlinks(self.target_dir.name, items)
        self.assertEqual(success, 0)
        self.assertEqual(errors, 1)

    def test_skip_same_directory(self):
        file_path = os.path.join(self.source_dir.name, "same.txt")
        with open(file_path, "w") as f:
            f.write("content")
        # Target directory is the same as source directory
        success, errors = pasteassymlink.create_symlinks(
            self.source_dir.name, [f"file://{file_path}"]
        )
        self.assertEqual(success, 0)
        self.assertEqual(errors, 1)

    @patch("os.symlink")
    def test_unexpected_symlink_os_error(self, mock_symlink):
        mock_symlink.side_effect = PermissionError("Permission denied")
        file_path = os.path.join(self.source_dir.name, "denied.txt")
        with open(file_path, "w") as f:
            f.write("content")
        success, errors = pasteassymlink.create_symlinks(
            self.target_dir.name, [f"file://{file_path}"]
        )
        self.assertEqual(success, 0)
        self.assertEqual(errors, 1)


class TestGetClipboard(unittest.TestCase):
    """Tests for get_clipboard backend resolution and fallback."""

    @patch("subprocess.run")
    def test_first_backend_succeeds(self, mock_run):
        mock_run.return_value = MagicMock(stdout="file:///tmp/test.txt\n")
        backend, text = pasteassymlink.get_clipboard()
        self.assertEqual(backend, "qdbus")
        self.assertEqual(text, "file:///tmp/test.txt")

    @patch("subprocess.run")
    def test_fallback_to_second_backend(self, mock_run):
        # First backend (qdbus) fails, second (wl-paste) succeeds
        mock_run.side_effect = [
            FileNotFoundError("qdbus not found"),
            MagicMock(stdout="file:///tmp/wayland.txt\n"),
        ]
        backend, text = pasteassymlink.get_clipboard()
        self.assertEqual(backend, "wl-paste")
        self.assertEqual(text, "file:///tmp/wayland.txt")

    @patch("subprocess.run")
    def test_backend_timeout_falls_back(self, mock_run):
        # First backend times out, second succeeds
        mock_run.side_effect = [
            subprocess.TimeoutExpired(cmd="qdbus", timeout=3),
            MagicMock(stdout="file:///tmp/timeout_fallback.txt\n"),
        ]
        backend, text = pasteassymlink.get_clipboard()
        self.assertEqual(backend, "wl-paste")
        self.assertEqual(text, "file:///tmp/timeout_fallback.txt")

    @patch("subprocess.run")
    def test_all_backends_fail(self, mock_run):
        mock_run.side_effect = FileNotFoundError("command not found")
        backend, text = pasteassymlink.get_clipboard()
        self.assertIsNone(backend)
        self.assertIsNone(text)


class TestNotify(unittest.TestCase):
    """Tests for desktop notification dispatching."""

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": ""}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_notify_send_called_when_available(self, mock_run, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/notify-send" if cmd == "notify-send" else None
        pasteassymlink.notify("Test Message", is_error=True)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "notify-send")
        self.assertIn("critical", args)
        self.assertIn("-i", args)
        self.assertIn("dialog-error", args)
        self.assertIn("Test Message", args)

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": ""}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_kdialog_called_when_notify_send_missing(self, mock_run, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/kdialog" if cmd == "kdialog" else None
        pasteassymlink.notify("Test Info", is_error=False)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "kdialog")
        self.assertIn("--icon", args)
        self.assertIn("special_paste-symbolic", args)
        self.assertIn("--passivepopup", args)
        self.assertIn("Test Info", args)

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": ""}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_custom_icon_used_if_provided(self, mock_run, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/notify-send" if cmd == "notify-send" else None
        pasteassymlink.notify("Custom Icon Message", icon="edit-paste")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("-i", args)
        self.assertIn("edit-paste", args)

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": "1"})
    @patch("subprocess.run")
    def test_notify_suppressed_when_env_var_set(self, mock_run):
        pasteassymlink.notify("Should not notify")
        mock_run.assert_not_called()

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": ""}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_notify_send_handles_exception_gracefully(self, mock_run, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/notify-send" if cmd == "notify-send" else None
        mock_run.side_effect = OSError("Subprocess failed")
        # Must not raise an exception
        pasteassymlink.notify("Error Msg")

    @patch.dict(os.environ, {"PASTEASSYMLINK_NO_NOTIFY": ""}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_kdialog_handles_exception_gracefully(self, mock_run, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/kdialog" if cmd == "kdialog" else None
        mock_run.side_effect = OSError("Subprocess failed")
        # Must not raise an exception
        pasteassymlink.notify("Info Msg", is_error=False)


class TestMain(unittest.TestCase):
    """Tests for main() entry point."""

    def test_no_arguments_exits_with_error(self):
        with patch.object(sys, "argv", ["pasteassymlink.py"]):
            with self.assertRaises(SystemExit) as cm:
                pasteassymlink.main()
            self.assertEqual(cm.exception.code, 1)

    def test_invalid_target_directory_exits(self):
        with patch.object(sys, "argv", ["pasteassymlink.py", "/non/existent/dir/12345"]):
            with self.assertRaises(SystemExit) as cm:
                pasteassymlink.main()
            self.assertEqual(cm.exception.code, 1)

    def test_empty_clipboard_exits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(sys, "argv", ["pasteassymlink.py", tmpdir]):
                with patch("pasteassymlink.get_clipboard", return_value=(None, None)):
                    with self.assertRaises(SystemExit) as cm:
                        pasteassymlink.main()
                    self.assertEqual(cm.exception.code, 1)

    def test_successful_main_execution(self):
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as tgt_dir:
            sample_file = os.path.join(src_dir, "test.txt")
            with open(sample_file, "w") as f:
                f.write("content")

            with patch.object(sys, "argv", ["pasteassymlink.py", tgt_dir]):
                with patch(
                    "pasteassymlink.get_clipboard",
                    return_value=("qdbus", f"file://{sample_file}"),
                ):
                    pasteassymlink.main()

            expected_link = os.path.join(tgt_dir, "test.txt")
            self.assertTrue(os.path.islink(expected_link))

    def test_main_failure_notification_when_source_not_found(self):
        with tempfile.TemporaryDirectory() as tgt_dir:
            with patch.object(sys, "argv", ["pasteassymlink.py", tgt_dir]):
                with patch(
                    "pasteassymlink.get_clipboard",
                    return_value=("qdbus", "file:///non/existent/item.txt"),
                ):
                    with patch("pasteassymlink.notify") as mock_notify:
                        pasteassymlink.main()
                        mock_notify.assert_called_with(
                            "Source file(s) not found.", is_error=True
                        )

    def test_main_failure_notification_same_directory(self):
        with tempfile.TemporaryDirectory() as src_dir:
            file_path = os.path.join(src_dir, "same.txt")
            with open(file_path, "w") as f:
                f.write("test")
            with patch.object(sys, "argv", ["pasteassymlink.py", src_dir]):
                with patch(
                    "pasteassymlink.get_clipboard",
                    return_value=("qdbus", f"file://{file_path}"),
                ):
                    with patch("pasteassymlink.notify") as mock_notify:
                        pasteassymlink.main()
                        mock_notify.assert_called_with(
                            "Cannot create symlinks in the same folder as the source file(s).",
                            is_error=True,
                        )

    def test_main_failure_notification_invalid_clipboard_text(self):
        with tempfile.TemporaryDirectory() as tgt_dir:
            with patch.object(sys, "argv", ["pasteassymlink.py", tgt_dir]):
                with patch(
                    "pasteassymlink.get_clipboard",
                    return_value=("qdbus", "not an absolute path text"),
                ):
                    with patch("pasteassymlink.notify") as mock_notify:
                        pasteassymlink.main()
                        mock_notify.assert_called_with(
                            "No valid file paths found on clipboard.",
                            is_error=True,
                        )


if __name__ == "__main__":
    unittest.main()
