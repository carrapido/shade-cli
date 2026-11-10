---
status: done
---

# Choose cache or a folder for the chapter PDF

## Spec

Reading compiles each chapter to a PDF in the cache (`~/.cache/shade-cli/`). Until now the app never said so, and there was no way to keep a copy anywhere else.

- When a chapter opens, the app prints the cached PDF's full path and says how to keep a copy.
- The reader menu gains **"Guardar PDF en carpeta…"**. It asks for a folder, prefilled with the download folder for that manga. Enter copies the PDF there and prints the full destination path. Esc cancels. Either way the reader menu comes back, so saving never moves you away from the chapter.
- Download folder: `$SHADE_DOWNLOAD_DIR/<Manga>` when the variable is set, else `~/Downloads/shade-cli/<Manga>`. `~` is expanded in both the variable and the typed answer.
- The folder is created when missing. If it cannot be created or written to, the app warns and keeps running.
- Saving works in terminal mode (`-t`) too: the PDF is compiled into the cache first.
- `-d` (CBZ download) writes into the same download folder instead of `./mangas/`, and prints the full destination before downloading.
- A chapter already in the cache opens without calling the API again.

## Tasks

- [x] Tests (RED): download folder, save action, cache message, `-d` destination.
- [x] `ensure_chapter_pdf()` (cache first, compile on miss) shared by reading and saving.
- [x] Reader menu "Guardar PDF en carpeta…" + `save_chapter_pdf()`.
- [x] `ask_text()` accepts a prefilled default (`fzf --query`).
- [x] `download_chapter()` uses the download folder.

## Log

### 2026-11-10 — done

- Outcome: `ensure_chapter_pdf()` returns the cached PDF, or compiles it on a miss (a cached chapter no longer calls the API). Opening a chapter prints the cache path and points to the menu option. The reader menu has "Guardar PDF en carpeta…": `save_chapter_pdf()` asks for a folder prefilled with `download_dir_for(manga)` (`$SHADE_DOWNLOAD_DIR/<manga>` or `~/Downloads/shade-cli/<manga>`), copies with `shutil.copy2`, prints the absolute path, warns on `OSError`, and returns to the menu. `-d` writes CBZ files into the same folder. 17 new tests; 40/40 green on Python 3.14 and 3.9.6. Tests were locked during implementation.
- Verified end to end in a pty with real fzf, the live API and an isolated `HOME`: save (prefilled folder, path printed, back to the menu), save then Esc (nothing copied, back to the menu), and `-d` (destination printed first, CBZ written, back to the chapter list).
- Behavior change: `-d` no longer writes to `./mangas/`.
- Found while testing (pre-existing, out of scope here): chapters are sorted by `orden` (upload order), so Berserk's list starts at Cap. 132. Added as objective 3.
- Pending checks: PDF mode on macOS Preview and on Linux viewers was covered by unit tests only (the e2e runs used `-t` to avoid opening a viewer).
- Next: objective 3, [Chapter list in reading order](chapter-order.md).
