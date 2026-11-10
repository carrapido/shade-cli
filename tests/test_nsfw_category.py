"""+18 NSFW results live in their own category. See odd/tasks/nsfw-category.md."""

import unittest
from unittest import mock

from shade_loader import shade

GENERAL = {"publicId": "g1", "titulo": "Boku no Hero Academia", "esMayorDeEdad": False}
UNFLAGGED = {"publicId": "u1", "titulo": "Sin bandera"}
ADULT_A = {"publicId": "a1", "titulo": "Boku No Hero Academia Doujinshi", "esMayorDeEdad": True}
ADULT_B = {"publicId": "a2", "titulo": "Lifeline Boku No Hero Academia", "esMayorDeEdad": True}


def listed(call) -> list:
    return call.args[0]


def adult_count(call) -> int:
    return call.kwargs.get("adult_count", 0)


class SplitByAgeRatingTest(unittest.TestCase):
    def test_separates_adult_titles_and_keeps_the_order(self):
        general, adult = shade.split_by_age_rating([GENERAL, ADULT_A, UNFLAGGED, ADULT_B])
        self.assertEqual(general, [GENERAL, UNFLAGGED])
        self.assertEqual(adult, [ADULT_A, ADULT_B])


class ResultsScreenTest(unittest.TestCase):
    def setUp(self):
        for name in ("print_info", "print_warn"):
            patcher = mock.patch.object(shade, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def browse(self, results, picks):
        with mock.patch.object(shade, "search_series", return_value=results), \
             mock.patch.object(shade, "pick_manga", side_effect=picks) as pick_manga, \
             mock.patch.object(shade, "browse_chapters") as browse_chapters:
            shade.browse_search_results("boku no hero", download_mode=False, terminal_mode=False)
        return pick_manga, browse_chapters

    def test_general_list_never_contains_adult_titles(self):
        pick_manga, _ = self.browse([GENERAL, ADULT_A, ADULT_B], picks=[None])
        first = pick_manga.call_args_list[0]
        self.assertEqual(listed(first), [GENERAL])
        self.assertEqual(adult_count(first), 2)

    def test_no_category_without_adult_results(self):
        pick_manga, _ = self.browse([GENERAL], picks=[None])
        self.assertEqual(adult_count(pick_manga.call_args_list[0]), 0)
        self.print_info.assert_any_call("Buscando 'boku no hero'...")
        messages = " ".join(str(c.args[0]) for c in self.print_info.call_args_list)
        self.assertNotIn("+18", messages)

    def test_tells_the_user_adult_results_are_kept_apart(self):
        self.browse([GENERAL, ADULT_A], picks=[None])
        messages = " ".join(str(c.args[0]) for c in self.print_info.call_args_list)
        self.assertIn("+18", messages)

    def test_category_opens_a_list_with_only_adult_titles(self):
        pick_manga, browse_chapters = self.browse(
            [GENERAL, ADULT_A, ADULT_B], picks=[shade.ADULT_CATEGORY, ADULT_A, None, None]
        )
        adult_list_call = pick_manga.call_args_list[1]
        self.assertEqual(listed(adult_list_call), [ADULT_A, ADULT_B])
        self.assertIn("+18", adult_list_call.kwargs["prompt"])
        self.assertEqual(browse_chapters.call_args.args[0], ADULT_A)

    def test_esc_in_the_adult_list_returns_to_the_general_results(self):
        pick_manga, _ = self.browse([GENERAL, ADULT_A], picks=[shade.ADULT_CATEGORY, None, None])
        self.assertEqual(pick_manga.call_count, 3)
        self.assertEqual(listed(pick_manga.call_args_list[2]), [GENERAL])

    def test_only_adult_results_still_offer_the_category(self):
        pick_manga, _ = self.browse([ADULT_A], picks=[None])
        first = pick_manga.call_args_list[0]
        self.assertEqual(listed(first), [])
        self.assertEqual(adult_count(first), 1)


class PickMangaCategoryTest(unittest.TestCase):
    def options_shown(self, mangas, **kwargs):
        with mock.patch.object(shade, "choose", return_value=None) as choose:
            shade.pick_manga(mangas, **kwargs)
        return choose.call_args.args[0], choose.call_args.kwargs["prompt"]

    def test_category_is_the_last_option_and_shows_the_count(self):
        options, _ = self.options_shown([GENERAL], adult_count=8)
        value, label = options[-1]
        self.assertIs(value, shade.ADULT_CATEGORY)
        self.assertIn("+18 NSFW", label)
        self.assertIn("8 resultados", label)
        self.assertEqual([v for v, _ in options[:-1]], [GENERAL])

    def test_singular_count(self):
        options, _ = self.options_shown([GENERAL], adult_count=1)
        self.assertIn("1 resultado ", options[-1][1] + " ")

    def test_no_category_option_without_adult_results(self):
        options, _ = self.options_shown([GENERAL])
        self.assertEqual([v for v, _ in options], [GENERAL])

    def test_prompt_can_be_changed_for_the_adult_list(self):
        _, prompt = self.options_shown([ADULT_A], prompt="+18 NSFW > ")
        self.assertEqual(prompt, "+18 NSFW > ")


if __name__ == "__main__":
    unittest.main()
