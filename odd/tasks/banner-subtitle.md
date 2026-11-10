---
status: done
---

# Banner subtitle

## Spec

Approved by the user on 2026-11-10: replace "Manga en terminal • Visor PDF nativo • Estilo ani-cli" with "Manga desde tu terminal · v<VERSION>". Same dim color and ASCII art.

- The version comes from `VERSION`, so it never drifts.
- `-v` / `--version` prints only `shade-cli v<VERSION>` (no banner), so the version is not printed twice and scripts can parse it.

## Tasks

- [x] Tests (RED).
- [x] Subtitle and `-v` output.

## Log

### 2026-11-10 — done

- Outcome: the banner subtitle reads "Manga desde tu terminal · v{VERSION}" (text approved by the user). `-v` prints only `shade-cli v1.1.0`. 3 new tests (RED before the change); 47/47 green on Python 3.14 and 3.9.6. Tests were locked during implementation.
- Verified: real `print_banner()` output under a pty, and `bin/shade-cli -v`.
- Pending checks: none.
- Next: objective 5, [README rewrite](readme.md).
