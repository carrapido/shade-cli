---
status: done
---

# Search tags: -nsfw and -<genre>

> "la categoria esta hasta abajo de los chats, sera dificil para el usuario que quiera consultar NFSW mangas si es que es una lista muy larga, haz que pueda usar etiquetas como -NSFW -[Categoria/generos]"

## Findings (live API, 2026-11-10)

- `/series-locales?genero=<name>` filters server side, case- and accent-insensitive (`Accion` = `Acción`), and combines with `q`. A comma-separated list is an AND (`Romance,Drama`: 30/30 have both). An unknown genre returns 0 results.
- No server-side adult filter (`adulto`, `nsfw`, `mayorDeEdad`, `esMayorDeEdad`, `soloAdultos` are ignored).
- `/series-locales/generos` lists 158 genres (`nombre`, `total`). Four names collide once accents and punctuation are removed (Shonen/Shōnen, Shojo/Shōjo, Shoujo-ai/Shoujo Ai, Shonen-ai/Shonen Ai).

## Spec

- In the search bar, a word that starts with `-` (and has more characters) is a tag; the other words are the title text. Tags are case-insensitive.
- `-nsfw`, `-18` or `-+18`: skip the general results and open the +18 list directly. No +18 results → warning, back to the search prompt.
- Any other tag is a genre. Hyphens inside it stand for spaces (`-boys-love` = Boys Love). It resolves against the genre catalog (fetched once per run) by name without accents or punctuation; on a collision the genre with more series wins. All genre tags go to the server as `genero=<A>,<B>` (AND), for the exact and the typo-tolerant search alike. Tags alone, without title text, list that genre.
- Unknown genre → warning with up to 3 close genres as tags (`¿Quisiste decir: -romance?`) and a pointer to `shade-cli --generos`; no search runs.
- `shade-cli --generos` prints every genre as `-tag  Name (N series)`, most series first, one line per tag.
- The search prompt header shows the tag syntax. The "+18 quedaron aparte" info line mentions `-nsfw`.

## Tasks

- [x] Tests (RED); adjust the objective-6 screen test for the new `search_series(text, genres)` call.
- [x] Parsing, genre resolution, `genero` parameter through exact and typo-tolerant search.
- [x] `--generos`, prompt hint, README, `-h`.

## Log

### 2026-11-10 — done

- Outcome: `parse_search_query()` splits the search bar into `SearchQuery(text, genre_tags, adult_only)`. `resolve_genres()` maps tags to catalog names via `genre_names_by_key()` (`fetch_genres()` is `functools.lru_cache`d; collisions keep the genre with more series) and warns with `difflib.get_close_matches` suggestions on an unknown one. `fetch_search_results(query, genres)` sends `genero=A,B` through the exact and the typo-tolerant search (`functools.partial` for the probes). `browse_search_results()` now dispatches to `browse_adult_only()` (-nsfw) or `browse_general_results()`. Also: `--generos` (`print_genre_tags()`), the tag hint in the search prompt's fzf header, `-h` epilog, README. 22 new tests plus one objective-6 test adjusted for the new call (all RED first, locked during implementation); 104/104 green on Python 3.14 and 3.9.6. Types use `collections.abc.Sequence`, not the deprecated `typing.Sequence`.
- Verified end to end in a pty with real fzf and the live API: hint shown in the search header; "boku no hero -nsfw" opens the +18 list directly; Esc returns to the search prompt; "-romanse" suggests "-romance" and searches nothing; "naruto -accion" lists Naruto; Ctrl-C exits 0. Live check: naruto + Acción → 9 results, all with Acción.
- Pending checks: `-nsfw` without a title or genre only sees the first page of the catalog (the API has no adult filter).
- Next: none; all objectives in the index are done.
