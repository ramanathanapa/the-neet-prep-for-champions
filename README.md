# NEET Paper Hub

A small local web page that catalogues **NEET UG question papers, answer keys and prep resources** in one place.
Each exam code (for example *NEET 2025 · Code 45*) is a card that pairs the question paper with its answer key and
solutions. Other pages (coaching sites, publisher hubs, Gulf-based coaching) are listed as links.

It does not store or display any questions or answers itself. It only links to the publishers.

## Features

- Papers grouped per exam year and code, question paper next to answer key.
- Filter by year, publisher or kind, plus free-text search.
- A **done** checkbox on every row, saved in a local DuckDB file.
- Optional local copies: if a PDF exists under `downloads/`, the title opens it; otherwise it opens the original site.

## Run it

```bash
pip install duckdb
python web.py
```

Open <http://localhost:8000>. On Windows use `py web.py`.

## Add or change links

Edit `sources.csv` and restart the server. Columns:

| column | meaning |
|---|---|
| `year` | exam year, or `all years` |
| `code` | exam booklet code (`45`, `T1`...); leave empty for general resources |
| `publisher` | who published it |
| `kind` | `question paper`, `answer key + solutions`, `paper + solutions`, `hub`, `coaching abroad` |
| `title` | text shown on the page |
| `url` | original link |
| `file` | optional local copy, relative to `downloads/` (for example `2025/NEET2025_Code45_paper.pdf`) |

`sources.csv` is the source of truth and is reloaded on every start. The `done` ticks live in `neet.duckdb` and are not
affected by CSV changes.

## Local PDF copies

The PDFs are copyrighted by their publishers, so `downloads/` is **not** in this repository. To use local copies,
download the PDFs yourself from the `url` column and save them under `downloads/` using the names in the `file` column.
Rows without a local file simply link to the original site. Keep any copies for your own practice and do not
redistribute them.

## Notes

- Single-user server on `127.0.0.1` using Python's built-in `http.server`. It has no login, so the done ticks are shared by
  anyone who can reach it. Do not expose it publicly if you keep copyrighted PDFs in `downloads/`.
- Links were checked for reachability when they were added. Sites move pages, so a link may break later.
- Not affiliated with NTA or any of the listed publishers.
