---
status: done
---

# +18 NSFW results in their own category

> "haz una categoria dentro de la busqueda que sean +18 NSFW y no mezcles los +18 NSFW con los mangas normales"

## Findings (live API, 2026-11-10)

Every search result carries a boolean `esMayorDeEdad`. It flags doujinshi, "R-18" and hentai titles: "boku no hero" returned 8 flagged out of 30, "shingeki" 3 of 30, "berserk" 0 of 11.

## Spec

- The search results screen lists only titles whose `esMayorDeEdad` is not `true`. A result without the field counts as general (there is no other signal).
- When the search also found +18 titles, the list ends with one entry, `+18 NSFW → N resultado(s) solo para adultos`, and an info line says they are kept apart. The entry goes last so Enter on the first item never opens it.
- Choosing that entry opens a list with only the +18 titles (prompt `+18 NSFW > `). Esc there returns to the general results; Enter opens the chapter list as usual.
- No +18 results → no entry and no info line. Only +18 results → the general list holds just the entry.
- Applies to exact and typo-tolerant searches alike (both go through `search_series()`).

## Tasks

- [x] Tests (RED).
- [x] `split_by_age_rating()`, `pick_manga(..., adult_count=)`, `browse_adult_results()`.
- [x] README.

## Log

### 2026-11-10 — done

- Outcome: `browse_search_results()` splits `search_series()` results with `split_by_age_rating()` (truthy `esMayorDeEdad` = adult). The general list goes to `pick_manga(general, adult_count=N)`, which appends a last `ADULT_CATEGORY` entry ("+18 NSFW → N resultado(s) solo para adultos") when N > 0. An info line announces the +18 results. Choosing the entry opens `browse_adult_results()` (prompt `+18 NSFW > `); Esc returns to the general results. README documents it. 11 new tests (9 RED before the change, 2 regression guards); 82/82 green on Python 3.14 and 3.9.6; tests locked during implementation.
- Verified end to end in a pty with real fzf and the live API ("boku no hero": 22 general, 8 +18): info line shown; fzf exact filter `'doujin` on the general list gives 0/23; "nsfw" + Enter opens the +18 list with the doujinshi titles; Esc returns to the general results; Ctrl-C exits 0.
- Pending checks: the split relies on the site's `esMayorDeEdad` flag; titles the site does not flag stay in the general list.
- Next: none; all objectives in the index are done.
