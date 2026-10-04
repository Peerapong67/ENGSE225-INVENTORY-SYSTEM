# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Console inventory management system (ENGSE225 course project) in Python 3.10+ and SQLite. It uses only the standard library at runtime. The code is a flat layout with no package: every module and test sits at the repo root and modules import each other by bare name. Comments, docstrings, user-facing strings and project docs are in **Thai**. Keep that convention when editing code.

## Commands

```bash
pip install -r requirements-dev.txt          # pytest, pytest-cov, flake8, bandit (same versions as CI)

python inventory_app.py                      # interactive menu (creates inventory.db in cwd on first run)
python inventory_app.py --selftest           # DoD self-test against inventory.db, cleans up after itself

python -m pytest -v                                          # all tests
python -m pytest test_inventory_app.py -v                    # one file
python -m pytest test_inventory_app.py::test_add_new_product_saves_and_logs -v   # one test
python -m pytest --cov --cov-report=term-missing             # coverage; fails below 90% (pyproject.toml)

python -m flake8 .                                           # reads .flake8 (max-line-length 120)
python -m bandit -c pyproject.toml -r .                      # -c is required, or B101 floods from test files
```

Each `test_*.py` can also run as `python test_xxx.py`, which prints a Thai "Terminal Demo" DoD table from its `__main__` block. That code is not exercised by pytest, so coverage omits test files.

CI (`.github/workflows/tests.yml`) runs on PRs and pushes to `main`/`develop`. It has two jobs:
- `pytest --cov` on Python 3.10, 3.11 and 3.12, with a 90% coverage gate
- a `lint` job that runs flake8 + bandit

PRs need all of these green. Branch flow: feature branch → PR into `develop` (CI green + QA approve) → `develop` into `main` (Tech Lead approve). See `documents/definition_of_done.md`.

## Architecture

The current app is `inventory_app.py` plus its supporting classes. The layers:

- **`InventoryApp`** is the console UI with menu items 1–8. It reads input through `Validator`, builds `Product` objects, calls `ProductRepository`, and logs every data-changing or reporting action through `Logger`. Tests assert the exact action names: `ADD_PRODUCT`, `UPDATE_PRODUCT`, `CUT_STOCK`, `SEARCH_PRODUCT`, `LOW_STOCK_ALERT_VIEWED` and `EXPORT_LOW_STOCK_CSV`. Results are shown with pagination, 10 per page.
- **`Validator`** has static input loops that re-prompt until the value is valid, plus the `confirm()` y/n prompt. Overwriting an existing product ID always asks for confirmation.
- **`Product`** is the entity. Its constructor validates its own fields: no empty ID or name, nothing negative. `is_low_stock()` returns `quantity <= reorder_point`.
- **`ProductRepository`** holds all SQL:
  - `upsertProduct` uses `INSERT … ON CONFLICT DO UPDATE` and rejects a non-empty barcode that another product already uses.
  - `updateStock` updates `products`, inserts a `stock_movements` row, then commits.
- **`DatabaseConnection`** and **`Logger`** are hand-rolled singletons. Call `getInstance()`; calling the constructor directly raises once an instance exists.
  - `DatabaseConnection.getInstance(db_name)` honors `db_name` **only on the first call**.
  - The connection uses `sqlite3.Row` and runs `schema.sql` on every connect. The schema is idempotent `CREATE … IF NOT EXISTS`, located through `__file__`, so it works from any cwd.
  - `ProductRepository()` and `Logger.log()` both pull the DB singleton implicitly, so creating `InventoryApp()` without a prior `getInstance(...)` opens `inventory.db` in the cwd.
- **`schema.sql`** is a second layer of defense behind the app checks:
  - CHECK constraints on quantity, price and reorder_point (no negatives)
  - a partial UNIQUE index on `barcode WHERE barcode != ''` (empty barcodes may repeat)
  - a FOREIGN KEY from `stock_movements`
  - a trigger that keeps `updated_at` current
- **`CsvReportExporter`** (CR-02) is static and knows nothing about the repository. It filters `is_low_stock()` itself and writes through **`AtomicFileWriter`**, which writes a temp file in the same directory, fsyncs it, then calls `os.replace`. A failed write leaves the old file untouched.

There are two different meanings of "low stock". Don't merge them:
- `getSummary()` and the report screen count `quantity <= LOW_STOCK_THRESHOLD`, a fixed 5.
- Alerts (menu 6) and the CSV export use each product's own `reorder_point` (CR-01 / BUG-102).

`app_v1.py` is the **legacy prototype**: a JSON file plus a global dict `x`. It is kept on purpose as the "before refactor" reference for `documents/risk_register_app_v1_emoji.md`. Don't refactor it. `test_app_v1.py` reads and writes `app_v1.x` directly.

## Process standards: ISO/IEC 12207 and ISO/IEC 14764

The course (ENGSE225 Software Evolution & Maintenance) frames every change through two standards:
- **ISO/IEC 12207** covers the software life cycle processes.
- **ISO/IEC 14764** covers the maintenance process inside that life cycle.

The repo's CR reports cite **ISO/IEC 14764:2006**. Keep citations consistent with that unless asked to update them, and don't invent clause numbers beyond the ones the existing reports already use.

### ISO/IEC 12207: where each life cycle process lives in this repo

| 12207 process | Artifact in this repo |
|---|---|
| Configuration management | Git branches `feature/*` / `bugfix/*` → `develop` → `main`, PRs, conventional commits |
| Risk management | `documents/risk_register_app_v1_emoji.md` (risk → mitigation → residual level) |
| Quality assurance | `documents/definition_of_done.md`, `documents/dod_per_feature.md`, the Flake8/Bandit gates, `reports/` |
| Verification | pytest unit + `test_integration.py`, coverage ≥ 90%, the CI matrix for Python 3.10–3.12 |
| Validation | Acceptance criteria and per-feature DoD; DoD §2 also requires one manual smoke test |
| Information management | Docstrings on every public method (DoD §4), README Change Request Log, `reports/*.md` |
| Maintenance | ISO/IEC 14764 workflow (below) and `documents/Change_Request_And_Impact_Analysis_Report*.md` |

### ISO/IEC 14764: workflow for any change to existing behavior

1. **Identify, classify and log** the change. Give it an ID (`CR-xx` for change requests, `BUG-xxx` for defects) and one 14764 maintenance category:
   - **Corrective:** fixes a reported fault (e.g. BUG-102 duplicate barcode). Commit prefix `fix:`.
   - **Adaptive:** keeps the software working in a changed environment, such as a Python version or a dependency. Commit prefix `build:`.
   - **Perfective:** a new feature or enhancement (e.g. CR-01 barcode/reorder point, CR-02 CSV export). Commit prefix `feat:`.
   - **Preventive:** fixes latent faults before they occur, such as the atomic write from the risk register, or lint/security hardening. Commit prefix `fix:`, `style:` or `test:`, depending on the change.
   - Urgent requests are marked **Emergency Change Request** and keep their base category, e.g. CR-02 is "Perfective (Expedited)".
2. **Impact analysis before coding.** For a CR, add `documents/Change_Request_And_Impact_Analysis_Report_CRxx.md` and copy the structure of the CR-01 and CR-02 reports:
   - Part 1: Identification & Logging, including business justification and scope
   - Part 2: Impact Analysis, with a traceability matrix (component → affected code → test impact) and an effort estimate
   - Part 3: Test-Driven Refinement plan, with a table of edge-case test cases
   - Then add the CR to the Change Request Log table in `README.md`.
3. **Trace the impact across the layers in this codebase.** Check each of:
   - UI menu and input sequence
   - `Validator`
   - `Product`
   - `ProductRepository` SQL
   - `schema.sql`: new columns need defaults for backward compatibility, as CR-01 did
   - `Logger` action names
   - CSV export
   - Every test that scripts the affected input sequence
4. **Implement test-first** on a branch cut from `develop`, following the Red → Green → Refactor cycle the CR reports specify. Keep the change inside the approved scope; don't add features the CR didn't ask for.
5. **Verify** (regression plus new tests): the full suite must pass, coverage must stay ≥ 90%, and Flake8 and Bandit must show 0 findings. If the change mitigates a risk, update the residual level in the risk register.
6. **Review and acceptance:** open a PR into `develop`. Merging needs CI green and QA approval; releasing to `main` needs Tech Lead approval. Leave approval and merge decisions to the humans in those roles.

## Testing notes

- In `conftest.py`, an autouse fixture resets both singletons before and after every test and closes the connection. Use the `db`/`repo` fixtures, which chdir into `tmp_path` and use `test_inventory.db`. Never let tests touch the real `inventory.db`.
- Interactive code is tested by monkeypatching `builtins.input` with a scripted list of answers. Each menu path consumes a fixed sequence of inputs. For example, menu 2 asks for: id, name, qty, price, category, barcode, reorder point, then `y`/`n` if the ID already exists.
- `test_integration.py` drives `InventoryApp.run()` and the real entry points (`runpy`) end-to-end with no mocked classes. Its input helper fails the test if the script runs out of answers.

## Conventions and gotchas

- The `__main__` self-test blocks use `_verify(cond, msg)` instead of `assert`, because Bandit B101 flags `assert` in non-test code. `assert` is fine only in `test_*.py` and `conftest.py`.
- Bandit skips B101 only in test files, and coverage omits test files. Both are configured in `pyproject.toml`. Don't add `# noqa`, `# nosec` or `# pragma: no cover`. The scan reports in `reports/` state that none are used.
- Source files use CRLF line endings, and the repo has `core.autocrlf=true`.
- Keep `requirements*.txt` ASCII-only. Older pip on Thai-locale Windows (cp874) can't decode UTF-8 Thai comments.
- Linter versions are pinned exactly in `requirements-dev.txt`. Test tools use bounded ranges in `requirements.txt`.
- The low-stock CSV is written as `utf-8-sig` (with a BOM) so Excel on Thai Windows reads Thai names (BUG-106). Read it back with `encoding="utf-8-sig"` in tests, or the first header cell becomes `\ufeffProductID`.
- `reports/` holds the generated scan and coverage reports and evidence. Flake8 and Bandit exclude it. `htmlcov/` is gitignored.
- Commit messages follow conventional prefixes: `feat:`, `fix:`, `test:`, `style:`, `docs:` and `build:`. They map to 14764 categories as listed above. Put the CR/BUG ID in the message when there is one.
