"""Chapters are listed in reading order. See odd/tasks/chapter-order.md."""

import unittest
from unittest import mock

from shade_loader import shade


def numbers_after_fetch(api_chapters):
    with mock.patch.object(shade, "make_api_request", return_value=api_chapters):
        return [c.get("numeroCapitulo") for c in shade.fetch_chapters("m1")]


class ChapterOrderTest(unittest.TestCase):
    def test_sorts_by_chapter_number_not_upload_order(self):
        api = [
            {"numeroCapitulo": 132, "orden": 1},
            {"numeroCapitulo": 0.001, "orden": 586},
            {"numeroCapitulo": 1.5, "orden": 3},
            {"numeroCapitulo": 1, "orden": 2},
        ]
        self.assertEqual(numbers_after_fetch(api), [0.001, 1, 1.5, 132])

    def test_numeric_strings_sort_as_numbers(self):
        api = [{"numeroCapitulo": "10", "orden": 1}, {"numeroCapitulo": "9", "orden": 2}]
        self.assertEqual(numbers_after_fetch(api), ["9", "10"])

    def test_same_number_keeps_upload_order(self):
        api = [
            {"numeroCapitulo": 5, "orden": 9, "publicId": "late"},
            {"numeroCapitulo": 5, "orden": 4, "publicId": "early"},
        ]
        with mock.patch.object(shade, "make_api_request", return_value=api):
            ids = [c["publicId"] for c in shade.fetch_chapters("m1")]
        self.assertEqual(ids, ["early", "late"])

    def test_chapter_without_a_number_goes_last(self):
        api = [{"numeroCapitulo": None, "orden": 1}, {"numeroCapitulo": "extra", "orden": 2}, {"numeroCapitulo": 3, "orden": 3}]
        self.assertEqual(numbers_after_fetch(api), [3, None, "extra"])


if __name__ == "__main__":
    unittest.main()
