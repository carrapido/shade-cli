"""The PDF stays in the cache unless you save it to a folder. See odd/tasks/pdf-save-location.md."""

import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from shade_loader import shade

CHAPTER = {"publicId": "c1", "numeroCapitulo": 7}
NEXT_CHAPTER = {"publicId": "c2", "numeroCapitulo": 8}


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shade_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for name in ("print_info", "print_warn", "print_success"):
            patcher = mock.patch.object(shade, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def cached_pdf(self) -> Path:
        pdf = self.tmp / "cache" / "Berserk - Cap 7.pdf"
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b"%PDF-1.4 test")
        return pdf

    def printed(self) -> str:
        calls = self.print_info.call_args_list + self.print_success.call_args_list + self.print_warn.call_args_list
        return "\n".join(str(c.args[0]) for c in calls)


class DownloadDirTest(unittest.TestCase):
    def test_defaults_to_downloads_folder_per_manga(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SHADE_DOWNLOAD_DIR", None)
            expected = Path.home() / "Downloads" / "shade-cli" / "Berserk"
            self.assertEqual(shade.download_dir_for("Berserk"), expected)

    def test_env_variable_overrides_the_base_folder(self):
        with mock.patch.dict(os.environ, {"SHADE_DOWNLOAD_DIR": "/srv/manga"}):
            self.assertEqual(shade.download_dir_for("Berserk"), Path("/srv/manga/Berserk"))

    def test_env_variable_expands_tilde(self):
        with mock.patch.dict(os.environ, {"SHADE_DOWNLOAD_DIR": "~/manga"}):
            self.assertEqual(shade.download_dir_for("Berserk"), Path.home() / "manga" / "Berserk")

    def test_manga_title_is_sanitized_for_the_file_system(self):
        with mock.patch.dict(os.environ, {"SHADE_DOWNLOAD_DIR": "/srv/manga"}):
            self.assertEqual(shade.download_dir_for("Fate/Zero: Kurozakura"), Path("/srv/manga/FateZero Kurozakura"))


class SaveChapterPdfTest(TempDirTestCase):
    def test_copies_the_cached_pdf_to_the_chosen_folder_and_prints_where(self):
        target = self.tmp / "elegida"
        with mock.patch.object(shade, "ensure_chapter_pdf", return_value=self.cached_pdf()), \
             mock.patch.object(shade, "ask_text", return_value=str(target)):
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        saved = target / "Berserk - Cap 7.pdf"
        self.assertEqual(saved.read_bytes(), b"%PDF-1.4 test")
        self.assertIn(str(saved), self.printed())

    def test_folder_prompt_is_prefilled_with_the_download_folder(self):
        with mock.patch.dict(os.environ, {"SHADE_DOWNLOAD_DIR": str(self.tmp / "base")}), \
             mock.patch.object(shade, "ensure_chapter_pdf", return_value=self.cached_pdf()), \
             mock.patch.object(shade, "ask_text", return_value=None) as ask:
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        self.assertEqual(ask.call_args.kwargs["default"], str(self.tmp / "base" / "Berserk"))

    def test_esc_on_folder_prompt_saves_nothing(self):
        with mock.patch.object(shade, "ensure_chapter_pdf", return_value=self.cached_pdf()), \
             mock.patch.object(shade, "ask_text", return_value=None), \
             mock.patch.object(shade.shutil, "copy2") as copy:
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        copy.assert_not_called()

    def test_typed_folder_expands_tilde(self):
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp)}), \
             mock.patch.object(shade, "ensure_chapter_pdf", return_value=self.cached_pdf()), \
             mock.patch.object(shade, "ask_text", return_value="~/mis-mangas"):
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        self.assertTrue((self.tmp / "mis-mangas" / "Berserk - Cap 7.pdf").exists())

    def test_unwritable_folder_warns_instead_of_crashing(self):
        blocker = self.tmp / "es-un-archivo"
        blocker.write_text("no soy carpeta")
        with mock.patch.object(shade, "ensure_chapter_pdf", return_value=self.cached_pdf()), \
             mock.patch.object(shade, "ask_text", return_value=str(blocker / "sub")):
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        self.print_warn.assert_called_once()

    def test_missing_pdf_skips_the_folder_prompt(self):
        with mock.patch.object(shade, "ensure_chapter_pdf", return_value=None), \
             mock.patch.object(shade, "ask_text") as ask:
            shade.save_chapter_pdf(CHAPTER, "Berserk")
        ask.assert_not_called()


class ReaderMenuSaveTest(unittest.TestCase):
    def test_reader_menu_offers_saving_the_pdf(self):
        options = shade.reader_menu_options(CHAPTER, [CHAPTER, NEXT_CHAPTER])
        self.assertIn(shade.SAVE_PDF, [value for value, _ in options])

    def test_saving_returns_to_the_reader_menu(self):
        with mock.patch.object(shade, "choose", side_effect=[shade.SAVE_PDF, NEXT_CHAPTER]) as choose, \
             mock.patch.object(shade, "save_chapter_pdf") as save:
            next_chapter = shade.pick_next_step(CHAPTER, [CHAPTER, NEXT_CHAPTER], manga_title="Berserk")
        save.assert_called_once_with(CHAPTER, "Berserk")
        self.assertEqual(choose.call_count, 2)
        self.assertIs(next_chapter, NEXT_CHAPTER)


class CachedPdfTest(TempDirTestCase):
    def test_opening_a_chapter_prints_the_cached_pdf_path(self):
        pdf = self.cached_pdf()
        with mock.patch.object(shade, "ensure_chapter_pdf", return_value=pdf), \
             mock.patch.object(shade, "open_file_in_system_viewer"):
            shade.read_in_pdf_mode(CHAPTER, "Berserk")
        self.assertIn(str(pdf), self.printed())

    def test_cached_chapter_opens_without_calling_the_api(self):
        with mock.patch.object(shade, "CACHE_DIR", self.tmp / "cache"), \
             mock.patch.object(shade, "fetch_chapter_pages") as fetch:
            pdf = self.cached_pdf()
            self.assertEqual(shade.ensure_chapter_pdf(CHAPTER, "Berserk"), pdf)
        fetch.assert_not_called()


class DownloadCbzTest(TempDirTestCase):
    def test_cbz_goes_to_the_download_folder_and_prints_where(self):
        page = self.tmp / "p_001.webp"
        page.write_bytes(b"img")
        with mock.patch.dict(os.environ, {"SHADE_DOWNLOAD_DIR": str(self.tmp / "base")}), \
             mock.patch.object(shade, "fetch_chapter_pages", return_value=["https://cdn/p1.webp"]), \
             mock.patch.object(shade, "download_pages_parallel", return_value=[page]):
            shade.download_chapter(CHAPTER, "Berserk")
        cbz = self.tmp / "base" / "Berserk" / "Berserk - Cap 7.cbz"
        self.assertEqual(zipfile.ZipFile(cbz).namelist(), ["p_001.webp"])
        self.assertIn(str(cbz.parent), self.printed())


class AskTextDefaultTest(unittest.TestCase):
    def test_fallback_uses_the_default_on_an_empty_answer(self):
        with mock.patch.object(shade, "has_fzf", return_value=False), \
             mock.patch("builtins.input", return_value=""):
            self.assertEqual(shade.ask_text("Carpeta > ", default="/srv/manga"), "/srv/manga")

    def test_fzf_prompt_is_prefilled_with_the_default(self):
        with mock.patch.object(shade, "has_fzf", return_value=True), \
             mock.patch.object(shade.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=1, stdout="/srv/manga\n\n")
            self.assertEqual(shade.ask_text("Carpeta > ", default="/srv/manga"), "/srv/manga")
        self.assertIn("--query=/srv/manga", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
