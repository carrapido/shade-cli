"""`shade-cli -h` matches the README. See odd/tasks/readme.md."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

from shade_loader import shade


def help_text() -> str:
    buffer = io.StringIO()
    with mock.patch.object(sys, "argv", ["shade-cli", "-h"]), redirect_stdout(buffer):
        with unittest.TestCase().assertRaises(SystemExit):
            shade.parse_arguments()
    return buffer.getvalue()


class HelpTest(unittest.TestCase):
    def test_drops_the_ani_cli_claim(self):
        self.assertNotIn("ani-cli", help_text())

    def test_download_flag_names_its_folder(self):
        self.assertIn("SHADE_DOWNLOAD_DIR", help_text())

    def test_explains_how_to_go_back_and_quit(self):
        text = help_text()
        self.assertIn("Esc", text)
        self.assertIn("Ctrl-C", text)

    def test_says_where_the_cache_lives(self):
        self.assertIn("~/.cache/shade-cli", help_text())


if __name__ == "__main__":
    unittest.main()
