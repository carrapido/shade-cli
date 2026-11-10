"""Search tags: -nsfw and -<genre>. See odd/tasks/search-tags.md."""

import io
import sys
import unittest
import urllib.parse
from contextlib import redirect_stdout
from unittest import mock

from shade_loader import shade

GENRE_CATALOG = [
    {"nombre": "Romance", "total": 23404},
    {"nombre": "Drama", "total": 16103},
    {"nombre": "Acción", "total": 9180},
    {"nombre": "Boys Love", "total": 6495},
    {"nombre": "Shōnen", "total": 140},
    {"nombre": "Shonen", "total": 654},
    {"nombre": "Yaoi (Soft)", "total": 40},
]
GENERAL = {"publicId": "g1", "titulo": "Naruto", "esMayorDeEdad": False}
ADULT = {"publicId": "a1", "titulo": "Naruto Doujinshi", "esMayorDeEdad": True}


def params(endpoint: str) -> dict:
    return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(endpoint).query, keep_blank_values=True).items()}


class GenreCatalogTestCase(unittest.TestCase):
    """Serves the genre catalog and records every other request."""

    def setUp(self):
        shade.fetch_genres.cache_clear()
        self.addCleanup(shade.fetch_genres.cache_clear)
        self.requests = []
        patcher = mock.patch.object(shade, "make_api_request", side_effect=self.fake_api)
        self.api = patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("print_info", "print_warn"):
            output = mock.patch.object(shade, name)
            setattr(self, name, output.start())
            self.addCleanup(output.stop)

    def fake_api(self, endpoint):
        if endpoint == "/series-locales/generos":
            return GENRE_CATALOG
        self.requests.append(params(endpoint))
        return [GENERAL, ADULT]

    def warnings(self) -> str:
        return " ".join(str(c.args[0]) for c in self.print_warn.call_args_list)


class ParseSearchQueryTest(unittest.TestCase):
    def test_words_starting_with_a_hyphen_are_tags(self):
        query = shade.parse_search_query("boku no hero -romance -nsfw")
        self.assertEqual(query.text, "boku no hero")
        self.assertEqual(query.genre_tags, ["romance"])
        self.assertTrue(query.adult_only)

    def test_tags_are_case_insensitive_and_have_aliases(self):
        for raw in ("naruto -NSFW", "naruto -18", "naruto -+18"):
            self.assertTrue(shade.parse_search_query(raw).adult_only, raw)

    def test_hyphens_inside_a_genre_tag_are_spaces(self):
        self.assertEqual(shade.parse_search_query("-boys-love").genre_tags, ["boys love"])

    def test_hyphenated_title_words_and_a_lone_hyphen_are_text(self):
        query = shade.parse_search_query("spider-man - x")
        self.assertEqual(query.text, "spider-man - x")
        self.assertEqual(query.genre_tags, [])
        self.assertFalse(query.adult_only)


class ResolveGenresTest(GenreCatalogTestCase):
    def test_no_tags_needs_no_catalog(self):
        self.assertEqual(shade.resolve_genres([]), [])
        self.api.assert_not_called()

    def test_matches_without_accents_case_or_punctuation(self):
        self.assertEqual(shade.resolve_genres(["accion", "BOYS LOVE", "yaoi soft"]), ["Acción", "Boys Love", "Yaoi (Soft)"])

    def test_collision_keeps_the_genre_with_more_series(self):
        self.assertEqual(shade.resolve_genres(["shonen"]), ["Shonen"])

    def test_unknown_genre_warns_with_suggestions_and_returns_none(self):
        self.assertIsNone(shade.resolve_genres(["romanse"]))
        self.assertIn("-romance", self.warnings())
        self.assertIn("--generos", self.warnings())

    def test_catalog_is_fetched_once_per_run(self):
        shade.resolve_genres(["romance"])
        shade.resolve_genres(["drama"])
        self.assertEqual(self.api.call_count, 1)


class GenreParameterTest(GenreCatalogTestCase):
    def test_genres_reach_the_server_as_one_comma_separated_filter(self):
        shade.fetch_search_results("naruto", ["Acción", "Romance"])
        self.assertEqual(self.requests, [{"q": "naruto", "genero": "Acción,Romance"}])

    def test_no_genres_sends_no_filter(self):
        shade.fetch_search_results("naruto")
        self.assertEqual(self.requests, [{"q": "naruto"}])

    def test_typo_tolerant_probes_keep_the_genre_filter(self):
        def empty_exact_search(endpoint):
            if endpoint == "/series-locales/generos":
                return GENRE_CATALOG
            self.requests.append(params(endpoint))
            return [] if params(endpoint).get("q") == "naurto" else [GENERAL]

        self.api.side_effect = empty_exact_search
        shade.search_series("naurto", ["Acción"])
        self.assertGreater(len(self.requests), 1)
        self.assertTrue(all(r.get("genero") == "Acción" for r in self.requests))


class TaggedSearchScreenTest(GenreCatalogTestCase):
    def browse(self, raw_query):
        with mock.patch.object(shade, "pick_manga", return_value=None) as pick_manga, \
             mock.patch.object(shade, "browse_adult_results") as adult_screen:
            shade.browse_search_results(raw_query, download_mode=False, terminal_mode=False)
        return pick_manga, adult_screen

    def test_nsfw_tag_opens_the_adult_list_directly(self):
        pick_manga, adult_screen = self.browse("naruto -nsfw")
        adult_screen.assert_called_once()
        self.assertEqual(adult_screen.call_args.args[0], [ADULT])
        pick_manga.assert_not_called()

    def test_nsfw_tag_without_adult_results_warns(self):
        self.api.side_effect = lambda endpoint: [GENERAL]
        _, adult_screen = self.browse("naruto -nsfw")
        adult_screen.assert_not_called()
        self.assertIn("+18", self.warnings())

    def test_genre_tags_alone_list_that_genre(self):
        self.browse("-romance")
        self.assertEqual(self.requests, [{"q": "", "genero": "Romance"}])

    def test_unknown_genre_skips_the_search(self):
        pick_manga, _ = self.browse("naruto -romanse")
        self.assertEqual(self.requests, [])
        pick_manga.assert_not_called()

    def test_adult_info_line_mentions_the_nsfw_tag(self):
        self.browse("naruto")
        messages = " ".join(str(c.args[0]) for c in self.print_info.call_args_list)
        self.assertIn("-nsfw", messages)


class SearchPromptHintTest(unittest.TestCase):
    def test_search_prompt_explains_the_tags(self):
        with mock.patch.object(shade, "ask_text", return_value=None) as ask:
            shade.ask_search_query()
        self.assertIn("-nsfw", ask.call_args.kwargs["hint"])

    def test_fzf_header_carries_the_hint_below_the_keys(self):
        with mock.patch.object(shade, "has_fzf", return_value=True), \
             mock.patch.object(shade.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=130, stdout="")
            shade.ask_text("Buscar manga > ", hint="Etiquetas: -nsfw")
        header = next(arg for arg in run.call_args.args[0] if arg.startswith("--header="))
        self.assertEqual(header, f"--header={shade.FZF_KEYS_HINT}\nEtiquetas: -nsfw")

    def test_fallback_prints_the_hint(self):
        printed = io.StringIO()
        with mock.patch.object(shade, "has_fzf", return_value=False), \
             mock.patch("builtins.input", return_value="naruto"), redirect_stdout(printed):
            shade.ask_text("Buscar manga > ", hint="Etiquetas: -nsfw")
        self.assertIn("Etiquetas: -nsfw", printed.getvalue())


class GenreListTest(GenreCatalogTestCase):
    def test_lists_tags_with_most_series_first(self):
        printed = io.StringIO()
        with mock.patch.object(sys, "argv", ["shade-cli", "--generos"]), redirect_stdout(printed):
            shade.main()
        lines = printed.getvalue().splitlines()
        self.assertTrue(lines[0].startswith("-romance"))
        self.assertIn("Romance", lines[0])
        self.assertIn("23404", lines[0])
        self.assertTrue(any(line.startswith("-yaoi-soft") for line in lines))

    def test_collisions_appear_once(self):
        printed = io.StringIO()
        with mock.patch.object(sys, "argv", ["shade-cli", "--generos"]), redirect_stdout(printed):
            shade.main()
        self.assertEqual(sum(1 for line in printed.getvalue().splitlines() if line.split()[0] == "-shonen"), 1)


if __name__ == "__main__":
    unittest.main()
