"""Esc goes back one screen; Ctrl-C quits. See odd/tasks/escape-navigation.md."""

import sys
import unittest
from unittest import mock

from shade_loader import shade

MANGA = {"publicId": "m1", "titulo": "Berserk", "autor": "Miura"}
FIRST = {"publicId": "c1", "numeroCapitulo": 1}
SECOND = {"publicId": "c2", "numeroCapitulo": 2}
THIRD = {"publicId": "c3", "numeroCapitulo": 3}


class FzfOutputTest(unittest.TestCase):
    def test_esc_on_a_list_means_go_back(self):
        self.assertIsNone(shade.parse_fzf_choice(130, ""))

    def test_enter_on_a_list_returns_the_selected_line(self):
        self.assertEqual(shade.parse_fzf_choice(0, "\n1\tBerserk\n"), "1\tBerserk")

    def test_ctrl_c_on_a_list_quits(self):
        with self.assertRaises(KeyboardInterrupt):
            shade.parse_fzf_choice(0, "ctrl-c\n1\tBerserk\n")

    def test_enter_on_a_text_prompt_returns_the_query(self):
        self.assertEqual(shade.parse_fzf_query(1, "chainsaw man\n\n"), "chainsaw man")

    def test_esc_on_a_text_prompt_means_go_back(self):
        self.assertIsNone(shade.parse_fzf_query(130, ""))

    def test_empty_text_prompt_means_go_back(self):
        self.assertIsNone(shade.parse_fzf_query(1, "\n\n"))

    def test_ctrl_c_on_a_text_prompt_quits(self):
        with self.assertRaises(KeyboardInterrupt):
            shade.parse_fzf_query(1, "chain\nctrl-c\n")


class ChooseTest(unittest.TestCase):
    OPTIONS = [("a", "Opción A"), ("b", "Opción B")]

    def test_fzf_selection_maps_back_to_its_value(self):
        with mock.patch.object(shade, "has_fzf", return_value=True), \
             mock.patch.object(shade, "run_fzf", return_value="1\tOpción B"):
            self.assertEqual(shade.choose(self.OPTIONS, prompt="> "), "b")

    def test_esc_in_fzf_returns_none(self):
        with mock.patch.object(shade, "has_fzf", return_value=True), \
             mock.patch.object(shade, "run_fzf", return_value=None):
            self.assertIsNone(shade.choose(self.OPTIONS, prompt="> "))

    def test_numbered_fallback_returns_the_typed_option(self):
        with mock.patch.object(shade, "has_fzf", return_value=False), \
             mock.patch("builtins.input", return_value="2"), \
             mock.patch("builtins.print"):
            self.assertEqual(shade.choose(self.OPTIONS, prompt="> "), "b")

    def test_q_in_numbered_fallback_returns_none(self):
        with mock.patch.object(shade, "has_fzf", return_value=False), \
             mock.patch("builtins.input", return_value="q"), \
             mock.patch("builtins.print"):
            self.assertIsNone(shade.choose(self.OPTIONS, prompt="> "))


class ScreenNavigationTest(unittest.TestCase):
    def setUp(self):
        for name in ("print_info", "print_warn", "print_success", "print_banner", "save_history"):
            patcher = mock.patch.object(shade, name)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_esc_on_search_prompt_exits(self):
        with mock.patch.object(shade, "ask_search_query", return_value=None), \
             mock.patch.object(shade, "browse_search_results") as results:
            shade.browse_from_search("", download_mode=False, terminal_mode=False)
        results.assert_not_called()

    def test_esc_on_search_results_returns_to_search_prompt(self):
        with mock.patch.object(shade, "ask_search_query", side_effect=["berserk", None]) as ask, \
             mock.patch.object(shade, "browse_search_results") as results:
            shade.browse_from_search("chainsaw", download_mode=False, terminal_mode=False)
        self.assertEqual([c.args[0] for c in results.call_args_list], ["chainsaw", "berserk"])
        self.assertEqual(ask.call_count, 2)

    def test_esc_on_chapter_list_returns_to_search_results(self):
        with mock.patch.object(shade, "fetch_search_results", return_value=[MANGA]), \
             mock.patch.object(shade, "pick_manga", side_effect=[MANGA, None]) as pick_manga, \
             mock.patch.object(shade, "fetch_chapters", return_value=[FIRST]), \
             mock.patch.object(shade, "pick_chapter", return_value=None):
            shade.browse_search_results("berserk", download_mode=False, terminal_mode=False)
        self.assertEqual(pick_manga.call_count, 2)

    def test_esc_on_reader_menu_returns_to_chapter_list(self):
        with mock.patch.object(shade, "fetch_chapters", return_value=[FIRST, SECOND]), \
             mock.patch.object(shade, "pick_chapter", side_effect=[FIRST, None]) as pick_chapter, \
             mock.patch.object(shade, "open_chapter") as open_chapter, \
             mock.patch.object(shade, "pick_next_step", return_value=None):
            shade.browse_chapters(MANGA, download_mode=False, terminal_mode=False)
        open_chapter.assert_called_once()
        self.assertEqual(pick_chapter.call_count, 2)

    def test_reader_menu_choice_opens_that_chapter(self):
        with mock.patch.object(shade, "fetch_chapters", return_value=[FIRST, SECOND]), \
             mock.patch.object(shade, "pick_chapter", side_effect=[FIRST, None]), \
             mock.patch.object(shade, "open_chapter") as open_chapter, \
             mock.patch.object(shade, "pick_next_step", side_effect=[SECOND, None]):
            shade.browse_chapters(MANGA, download_mode=False, terminal_mode=False)
        opened = [c.args[0] for c in open_chapter.call_args_list]
        self.assertEqual(opened, [FIRST, SECOND])

    def test_continue_opens_the_saved_chapter_without_asking(self):
        with mock.patch.object(shade, "fetch_chapters", return_value=[FIRST, SECOND]), \
             mock.patch.object(shade, "pick_chapter", return_value=None), \
             mock.patch.object(shade, "open_chapter") as open_chapter, \
             mock.patch.object(shade, "pick_next_step", return_value=None):
            shade.browse_chapters(MANGA, initial_chapter_id="c2", download_mode=False, terminal_mode=False)
        self.assertEqual(open_chapter.call_args.args[0], SECOND)

    def test_download_mode_returns_to_chapter_list_after_each_download(self):
        with mock.patch.object(shade, "fetch_chapters", return_value=[FIRST, SECOND]), \
             mock.patch.object(shade, "pick_chapter", side_effect=[FIRST, SECOND, None]) as pick_chapter, \
             mock.patch.object(shade, "download_chapter") as download:
            shade.browse_chapters(MANGA, download_mode=True, terminal_mode=False)
        self.assertEqual(download.call_count, 2)
        self.assertEqual(pick_chapter.call_count, 3)

    def test_esc_after_continue_lands_on_search_prompt(self):
        history = {"last_manga": MANGA, "last_chapter_id": "c1"}
        calls = []
        with mock.patch.object(sys, "argv", ["shade-cli", "-c"]), \
             mock.patch.object(shade, "load_history", return_value=history), \
             mock.patch.object(shade, "browse_chapters", side_effect=lambda *a, **k: calls.append("chapters")), \
             mock.patch.object(shade, "browse_from_search", side_effect=lambda *a, **k: calls.append("search")):
            shade.main()
        self.assertEqual(calls, ["chapters", "search"])


class ReaderMenuTest(unittest.TestCase):
    def labels(self, chapter, chapters):
        return " | ".join(label for _, label in shade.reader_menu_options(chapter, chapters))

    def test_first_chapter_offers_next_but_not_previous(self):
        labels = self.labels(FIRST, [FIRST, SECOND])
        self.assertIn("Siguiente", labels)
        self.assertNotIn("Anterior", labels)

    def test_last_chapter_offers_previous_but_not_next(self):
        labels = self.labels(SECOND, [FIRST, SECOND])
        self.assertIn("Anterior", labels)
        self.assertNotIn("Siguiente", labels)

    def test_next_option_points_to_the_following_chapter(self):
        options = dict((label, value) for value, label in shade.reader_menu_options(SECOND, [FIRST, SECOND, THIRD]))
        next_label = next(label for label in options if label.startswith("Siguiente"))
        self.assertIs(options[next_label], THIRD)

    def test_quit_option_exits_the_app(self):
        with mock.patch.object(shade, "choose", return_value=shade.QUIT), \
             mock.patch("builtins.print"):
            with self.assertRaises(SystemExit):
                shade.pick_next_step(FIRST, [FIRST, SECOND], manga_title="Berserk")


if __name__ == "__main__":
    unittest.main()
