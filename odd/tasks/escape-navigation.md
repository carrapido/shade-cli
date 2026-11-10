---
status: done
---

# Esc goes back one screen

## Spec

Screens form a stack: search prompt → search results → chapter list → reader menu.

- Esc on any screen returns to the previous one; Esc on the search prompt exits.
- Ctrl-C on any screen exits the app.
- After a chapter opens, the reader menu is an fzf list (Next, Reopen, Previous, Pick another chapter, Quit) instead of a typed letter, so Esc works there too.
- `-c` (continue) opens the reader directly; Esc from its chapter list lands on the search prompt.
- `-d` (download) returns to the chapter list after each download, so several chapters can be saved in one session.
- Without fzf, the numbered-list fallback keeps working: `q` or an empty answer goes back.

## Tasks

- [x] Tests (RED): fzf output interpretation and screen-to-screen navigation.
- [x] One `choose()` picker shared by manga list, chapter list and reader menu.
- [x] Nested screen loops where `None` means "go back".

## Log

### 2026-11-10 — done

- Outcome: screens are nested loops (`browse_from_search` → `browse_search_results` → `browse_chapters` → `read_from`); a picker returning `None` (Esc) ends the loop and hands control back. One `choose()` serves the three lists and the numbered fallback. fzf runs with `--expect=ctrl-c`, so Esc (exit 130) means back and Ctrl-C means quit. The reader menu is now an fzf list. `make test` runs `tests/` (23 tests, green on Python 3.14 and 3.9.6).
- Verified end to end in a pty with real fzf and the live API: search → results → chapters → Esc → results → Esc → search → Ctrl-C (exit 0); and with `-t`: reader menu → Esc → chapters → Esc → results.
- Pending checks: run it on Arch (fzf from pacman); the numbered fallback without fzf was covered only by unit tests.
- Next: objective 2, [Choose cache or a folder for the chapter PDF](pdf-save-location.md).
