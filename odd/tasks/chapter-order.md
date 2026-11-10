---
status: done
---

# Chapter list in reading order

## Spec

`fetch_chapters()` sorted by `orden`, which follows upload order, not reading order. Berserk's list started at Cap. 132, its 0.x chapters sat at the end, and "Siguiente" followed upload order.

- Chapters are sorted by `numeroCapitulo` as a number (decimals included: 0.001 < 0.01 < 1 < 1.5 < 2 < 10).
- `numeroCapitulo` may arrive as a number or a numeric string; both sort numerically.
- Chapters with the same number (for example, two scan groups) keep `orden` as the tie-breaker.
- A chapter without a usable number goes to the end of the list instead of breaking the sort.

## Tasks

- [x] Tests (RED) for the sort.
- [x] Sort key `reading_order()`.

## Log

### 2026-11-10 — done

- Outcome: `fetch_chapters()` sorts with `reading_order()` = (`chapter_number()`, `orden`). `chapter_number()` parses `numeroCapitulo` with `float()` and returns `math.inf` for missing or non-numeric values, so those go last. 4 new tests (3 RED before the change; the tie-break test already passed and stays as a regression guard). 44/44 green on Python 3.14 and 3.9.6. Tests were locked during implementation.
- Verified against the live API: Berserk now lists 0.001, 0.01, … 384, 385, 386; after 132 comes 133.
- Pending checks: none.
- Next: objective 4, [Banner subtitle](banner-subtitle.md).
