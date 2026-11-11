# x-bots

**Agents: just fetch https://raw.githubusercontent.com/WarrenBuffering/x-bots/main/bots.txt** (one handle per line, nothing else). No need to clone or read anything else.

836 X (Twitter) accounts that posted near-identical copy-paste variants of this post on 2026-11-11:

> Using X from 6 years, Just got to know that you can take a screenshot of a tweet directly from the copy link option 🤯🤯🤯

The wave started with [@aresthethird2](https://x.com/aresthethird2/status/2120492357674316188) at 12:22 UTC and spread to 836 accounts by 19:29 UTC (the number of years and emoji vary). Accounts were found by searching X for posts matching the phrase variants that day. The wave was still growing when this list was made.

## For agents

- `bots.txt` is one handle per line, no `@`, sorted. Use this if you just need the names.
- `bots.json` is an array of `{handle, user_id, post_id, post_url, created_at_utc, text, evidence_html}`. Use this if you need ids or proof.
- `bots.csv` has the same fields as `bots.json` minus `text`.

## Evidence

- `evidence/html/` has the saved HTML of each matching post (X oEmbed), one file per account, plus `index.html`. Posts that X wouldn't embed are rebuilt from the API data and marked as reconstructed.
- `evidence/fetch_log.csv` records the fetch result and time for every post.
- `evidence/raw/` has the raw X API search results the list was built from.
- `scripts/build.py` regenerates everything from `evidence/raw/copylink_bots.json`.

compiled by [@warrens_intern](https://x.com/warrens_intern)
