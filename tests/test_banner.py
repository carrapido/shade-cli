"""Banner subtitle and --version output. See odd/tasks/banner-subtitle.md."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

from shade_loader import shade


def captured(action) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        action()
    return buffer.getvalue()


class BannerTest(unittest.TestCase):
    def test_subtitle_names_the_app_purpose_and_version(self):
        self.assertIn(f"Manga desde tu terminal · v{shade.VERSION}", captured(shade.print_banner))

    def test_subtitle_drops_the_old_claims(self):
        banner = captured(shade.print_banner)
        self.assertNotIn("ani-cli", banner)
        self.assertNotIn("Visor PDF nativo", banner)

    def test_version_flag_prints_only_the_version(self):
        with mock.patch.object(sys, "argv", ["shade-cli", "-v"]):
            self.assertEqual(captured(shade.main), f"shade-cli v{shade.VERSION}\n")


if __name__ == "__main__":
    unittest.main()
