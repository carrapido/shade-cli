---
status: done
---

# AUR and Homebrew publishing issue

## Spec

The user wants shade-cli on the AUR and Homebrew later, but not published now. The publishing steps go in a GitHub issue, not in the README. The README only says the packages are coming and links the issue.

## Log

### 2026-11-10 — done

- Outcome: created https://github.com/carrapido/shade-cli/issues/1 (`chore: publish shade-cli to the AUR and Homebrew`). It covers release prerequisites (tag v1.2.0, fix the in-repo PKGBUILD), AUR steps with a draft PKGBUILD (tarball source, `make install`, `check()` running `make test`), and a Homebrew personal tap with a draft formula (`rewrite_shebang detected_python_shebang`, `python@3.15`, fzf, graphicsmagick). Each step cites the official page. The README line links #1.
- Sources: Arch wiki read through `index.php?...&action=raw` (the HTML pages are behind Anubis bot protection for automated fetches); Homebrew docs and their markdown source on GitHub; `detected_python_shebang` confirmed in local Homebrew 7.0.12 source (`Library/Homebrew/language/python.rb`); the Arch package names and `shade-cli` name availability confirmed through the archlinux.org and AUR JSON APIs.
- Findings now in the issue: `python-img2pdf` in the current PKGBUILD does not exist (the package is `img2pdf`); `timg` is not in the official repos; PKGBUILD `url` points to `crpd`.
- Pending checks: nothing has been built on Arch or installed from a tap; the drafts are untested until a v1.2.0 tag exists.
- Next: none. All objectives in the index are done.
