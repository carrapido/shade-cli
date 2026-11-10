---
status: done
---

# Typo-tolerant search

> "quiero que la barra de busqueda haga busqueda por aproximaciones de la palabra y no el por la palabra exacta asi para que el usuario pueda hacer typos y no tenga tantos problemas"

## Findings (live API, 2026-11-10)

- `/series-locales?q=` matches substrings only: "berse" finds Berserk, "berzerk", "bersek", "chainsawman", "one pice" find nothing.
- Results are paginated (30 per page). The catalog has ~48,700 series (1,625 pages), so downloading it for local fuzzy search is not an option.
- For short pieces (3–5 letters) the server lists titles that start with the piece first; the intended title was on page 1 in all 10 probes.
- The server answers HTTP 429 when flooded (hit after ~100 requests in about a minute).

## Spec

- The exact search runs first; when it finds series, nothing changes.
- When it finds nothing, the app says so and runs a typo-tolerant search:
  - Probes, most specific first, at most 8: the phrase without its last word and without its first word (2+ words); the start and end of each word of 3+ letters (length `max(3, (len-1)//2)`, so a typo in the middle leaves at least one intact); for a single word, that word with each pair of neighbouring letters swapped ("naurto" → "naruto").
  - Probes run 4 at a time. Results are merged without duplicates.
  - Each title gets (best match of the query against any same-length slice of the title, match against the whole title) with `difflib.SequenceMatcher`, after lowercasing and removing accents and punctuation. Titles under 0.75 are dropped (calibrated live: intended titles scored ≥ 0.82, unrelated ones ≤ 0.69). Best first; ties go to the title closest to the whole query.
  - A probe that fails (HTTP 429, network) counts as empty. If every probe fails, the app warns that the server could not be reached.
- Calibration set (all must put the intended title first): berzerk, bersek, chainsawman, one pice, oyasumi punpn, chensaw man, naurto, bleack, kimetsu no yaibs, jujutsu kaizn, boku no hero academy.

## Tasks

- [x] Tests (RED) with a fake substring-search server.
- [x] `search_series()` → `find_similar_series()` → probes, ranking, normalization.
- [x] README: mention that typos are tolerated.

## Log

### 2026-11-10 — done

- Outcome: `browse_search_results()` calls `search_series()`: exact search first (one request, unchanged behavior on a hit); on zero results it announces the approximate search and runs `find_similar_series()` → `search_probes()` (phrase / word-edge / swapped-letter probes, at most 8, ≥ 3 letters) → `fetch_probe_results()` (4 parallel, failed probe = None via `try_fetch_search_results()`) → `unique_series()` → `rank_by_similarity()` (`difflib.SequenceMatcher` slice and whole ratios on `normalize_title()`, cutoff 0.75). All probes failing → warning, no traceback. README documents it. 20 new tests against a fake substring-search server (RED first, locked during implementation); 71/71 green on Python 3.14 and 3.9.6.
- Verified against the live API through `search_series()`: all 11 calibration queries put the intended title first, 0.9–1.5 s and ≤ 9 requests each, no 429. End to end in a pty with real fzf: "naurto" → approximate notice → Naruto listed → Esc → search prompt → Ctrl-C (exit 0).
- Pending checks: the rate limit threshold is unknown (429 seen after ~100 requests/minute while probing); requests outside the typo search (exact search, chapters, pages) still raise on HTTP errors, as before this change.
- Next: objective 7, [AUR and Homebrew publishing issue](publishing-issue.md).
