---
status: done
---

# README rewrite

## Spec

The README documents the app as it is now, for someone installing it for the first time. It stays in Spanish because the app's UI and its audience (shademanga.com readers) are Spanish-speaking.

- Accurate install (macOS and Arch/Linux via `make install`, with dependencies), usage, keys per screen, flags, where files live (cache, saved PDFs, CBZ, history), environment variables, troubleshooting, uninstall, development (`make test`).
- No packaging or publishing instructions for AUR or Homebrew: those go in the GitHub issue (objective 6). The README only says that the packages are coming.
- No unverified claims (removed "menos de 1 segundo", "Cero anuncios", "Visor PDF nativo", "Estilo ani-cli").
- Real repository URL (`carrapido/shade-cli`) instead of `TU_USUARIO`.
- `shade-cli -h` tells the same story: no "estilo ani-cli", `-d` names its folder, and the epilog shows Esc / Ctrl-C and where the cache lives.

## Tasks

- [x] Tests (RED) for `-h`.
- [x] `-h` texts.
- [x] README.

## Log

### 2026-11-10 — done

- Outcome: README rewritten in Spanish (requirements table; install for macOS, Arch, other Linux and without sudo; update/uninstall; screens and keys; reader menu; flags; file locations; environment variables; troubleshooting; development; notice). Real repo URL, no publishing steps, no unverified claims. `-h` aligned: new description, flag texts, and a raw-formatted epilog with keys and file paths (argparse `RawDescriptionHelpFormatter`, so paths do not wrap at hyphens). 4 new tests for `-h` (RED before the change); 51/51 green on Python 3.14 and 3.9.6.
- Verified: `make install`/`uninstall` with `DESTDIR` and with `PREFIX="$HOME/.local"` under an isolated `HOME` (zsh -f); every flag, key and path in the README checked against the code.
- Pending checks: GitHub anchor links and table rendering on github.com after a push; Arch package names (`graphicsmagick`, `zathura-pdf-mupdf`) not checked on an Arch machine.
- Next: objective 6, [AUR and Homebrew publishing issue](publishing-issue.md). The README line "Los paquetes para AUR y Homebrew están en preparación" should link to that issue once it exists.
