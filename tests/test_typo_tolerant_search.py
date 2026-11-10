"""Search tolerates typos. See odd/tasks/typo-tolerant-search.md."""

import unittest
import urllib.error
import urllib.parse
from unittest import mock

from shade_loader import shade

CATALOG = [
    "Berserk", "Berserk Of Gluttony", "Bermuda", "Berry Dynamite", "Another Happy Ending With My Jerk Friend",
    "Naruto", "Naruto Gaiden", "Concerto", "Dragonaut",
    "One Piece", "One Punch Man", "Gakuen Police",
    "Chainsaw Man", "Chain Chronicle Crimson",
    "Oyasumi Punpun", "Oyasumi, Fumi-san",
    "Boku no Hero Academia", "Boku No Omega Yo Samenaide", "Love Academy",
    "Bleach", "Black Box",
    "Pokémon Adventures",
]


class FakeServer:
    """Mimics /series-locales?q=: case-insensitive substring match, accents kept as they are."""

    def __init__(self):
        self.queries = []

    def __call__(self, endpoint):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(endpoint).query)["q"][0]
        self.queries.append(query)
        return [{"publicId": title, "titulo": title} for title in CATALOG if query.lower() in title.lower()]


class TypoTolerantSearchTest(unittest.TestCase):
    def setUp(self):
        for name in ("print_info", "print_warn"):
            patcher = mock.patch.object(shade, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def search(self, query, server=None):
        self.server = server or FakeServer()
        with mock.patch.object(shade, "make_api_request", self.server):
            return [m["titulo"] for m in shade.search_series(query)]

    def assert_first(self, query, expected):
        titles = self.search(query)
        self.assertTrue(titles, f"{query!r} found nothing")
        self.assertEqual(titles[0], expected, f"{query!r} → {titles}")

    def test_exact_match_uses_a_single_request(self):
        self.assertEqual(self.search("berserk"), ["Berserk", "Berserk Of Gluttony"])
        self.assertEqual(self.server.queries, ["berserk"])

    def test_wrong_letter(self):
        self.assert_first("berzerk", "Berserk")

    def test_missing_letter(self):
        self.assert_first("one pice", "One Piece")

    def test_swapped_letters(self):
        self.assert_first("naurto", "Naruto")

    def test_missing_space(self):
        self.assert_first("chainsawman", "Chainsaw Man")

    def test_typo_in_the_second_word(self):
        self.assert_first("oyasumi punpn", "Oyasumi Punpun")

    def test_different_last_word(self):
        self.assert_first("boku no hero academy", "Boku no Hero Academia")

    def test_ties_go_to_the_title_closest_to_the_whole_query(self):
        self.assert_first("bleack", "Bleach")

    def test_accents_and_case_are_ignored_when_ranking(self):
        self.assert_first("POKEMON adventurs", "Pokémon Adventures")

    def test_unrelated_titles_are_left_out(self):
        titles = self.search("berzerk")
        self.assertNotIn("Bermuda", titles)
        self.assertNotIn("Another Happy Ending With My Jerk Friend", titles)

    def test_nothing_similar_returns_no_results(self):
        self.assertEqual(self.search("zzqqxx"), [])

    def test_tells_the_user_the_results_are_approximate(self):
        self.search("berzerk")
        messages = " ".join(str(c.args[0]) for c in self.print_info.call_args_list)
        self.assertIn("parecidos", messages)

    def test_server_errors_on_every_probe_warn_instead_of_crashing(self):
        def rate_limited_after_the_exact_search(endpoint):
            if endpoint.endswith("q=berzerk"):
                return []
            raise urllib.error.HTTPError(endpoint, 429, "Too Many Requests", {}, None)

        self.assertEqual(self.search("berzerk", server=rate_limited_after_the_exact_search), [])
        self.print_warn.assert_called_once()

    def test_a_failed_probe_does_not_hide_the_others(self):
        server = FakeServer()

        def flaky(endpoint):
            if "q=erk" in endpoint:
                raise urllib.error.HTTPError(endpoint, 429, "Too Many Requests", {}, None)
            return server(endpoint)

        self.assertEqual(self.search("berzerk", server=flaky)[0], "Berserk")


class SearchProbesTest(unittest.TestCase):
    def test_start_and_end_of_each_word(self):
        probes = shade.search_probes("berzerk")
        self.assertIn("ber", probes)
        self.assertIn("erk", probes)

    def test_single_word_gets_neighbour_letters_swapped(self):
        self.assertIn("naruto", shade.search_probes("naurto"))

    def test_phrases_without_the_last_and_the_first_word_come_first(self):
        self.assertEqual(shade.search_probes("boku no hero academy")[:2], ["boku no hero", "no hero academy"])

    def test_never_more_than_eight_probes(self):
        self.assertLessEqual(len(shade.search_probes("un titulo larguisimo con muchisimas palabras distintas")), 8)

    def test_no_duplicates_or_pieces_shorter_than_three_letters(self):
        probes = shade.search_probes("aaa no aaa")
        self.assertEqual(len(probes), len(set(probes)))
        self.assertTrue(all(len(p) >= 3 for p in probes))


class SearchScreenTest(unittest.TestCase):
    def test_search_results_screen_uses_the_typo_tolerant_search(self):
        with mock.patch.object(shade, "search_series", return_value=[{"publicId": "m1", "titulo": "Naruto"}]) as search, \
             mock.patch.object(shade, "pick_manga", return_value=None), \
             mock.patch.object(shade, "print_info"):
            shade.browse_search_results("naurto", download_mode=False, terminal_mode=False)
        search.assert_called_once_with("naurto")


if __name__ == "__main__":
    unittest.main()
