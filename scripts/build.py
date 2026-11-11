#!/usr/bin/env python3
"""Regenerate x-bots files from evidence/raw/copylink_bots.json and fetch post HTML via X oEmbed."""
import json, csv, os, time, html, urllib.request, urllib.parse, urllib.error, datetime, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'evidence', 'raw', 'copylink_bots.json')
HTML_DIR = os.path.join(ROOT, 'evidence', 'html')
os.makedirs(HTML_DIR, exist_ok=True)
rows = json.load(open(RAW))
seen = {}
for r in rows:
    seen.setdefault(r['username'].lower(), r)
rows = sorted(seen.values(), key=lambda r: r['username'].lower())
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
log = []
skip_fetch = '--no-fetch' in sys.argv
for i, r in enumerate(rows):
    h, pid = r['username'], r['post_id']
    url = f'https://x.com/{h}/status/{pid}'
    path = os.path.join(HTML_DIR, f'{h}_{pid}.html')
    r['evidence_html'] = f'evidence/html/{h}_{pid}.html'
    if os.path.exists(path) and skip_fetch:
        continue
    status, body = None, None
    if not skip_fetch:
        q = 'https://publish.twitter.com/oembed?' + urllib.parse.urlencode({'url': url, 'omit_script': 'true', 'dnt': 'true'})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(q, headers={'User-Agent': 'x-bots-evidence/1.0'}), timeout=20) as resp:
                    body = json.load(resp)['html']; status = 'oembed_ok'; break
            except urllib.error.HTTPError as e:
                status = f'http_{e.code}'
                if e.code in (429, 500, 502, 503, 504): time.sleep(5 * (attempt + 1)); continue
                break
            except Exception as e:
                status = f'error_{type(e).__name__}'; time.sleep(3 * (attempt + 1))
        time.sleep(1)
    t = now()
    if body:
        page = f'<!doctype html>\n<!-- source: {url} | fetched via X oEmbed at {t} -->\n<html><head><meta charset="utf-8"><title>@{h} {pid}</title></head><body>\n{body}\n</body></html>\n'
    else:
        page = (f'<!doctype html>\n<!-- reconstructed from API data, oEmbed unavailable: {status} | source: {url} | written {t} -->\n'
                f'<html><head><meta charset="utf-8"><title>@{h} {pid}</title></head><body>\n'
                f'<p><strong>reconstructed from API data, oEmbed unavailable: {html.escape(str(status))}</strong></p>\n'
                f'<blockquote><p>{html.escape(r["text"]).replace(chr(10), "<br>")}</p>\n'
                f'<p>@{h} (user id {r["user_id"]}) · {r["created_at_utc"]} · <a href="{url}">{url}</a></p></blockquote>\n</body></html>\n')
    open(path, 'w').write(page)
    log.append((h, pid, status, t))
    if i % 50 == 0: print(i, h, status, flush=True)
with open(os.path.join(HTML_DIR, 'index.html'), 'w') as f:
    f.write('<!doctype html><html><head><meta charset="utf-8"><title>x-bots evidence</title></head><body><h1>x-bots evidence</h1><ol>\n')
    for r in rows:
        f.write(f'<li><a href="{r["username"]}_{r["post_id"]}.html">@{r["username"]}</a> · <a href="https://x.com/{r["username"]}/status/{r["post_id"]}">post</a></li>\n')
    f.write('</ol></body></html>\n')
if log:
    with open(os.path.join(ROOT, 'evidence', 'fetch_log.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['handle', 'post_id', 'status', 'fetched_at_utc']); w.writerows(log)
open(os.path.join(ROOT, 'bots.txt'), 'w').write('\n'.join(r['username'] for r in rows) + '\n')
out = [{'handle': r['username'], 'user_id': r['user_id'], 'post_id': r['post_id'], 'post_url': f'https://x.com/{r["username"]}/status/{r["post_id"]}',
        'created_at_utc': r['created_at_utc'], 'text': r['text'], 'evidence_html': r['evidence_html']} for r in rows]
json.dump(out, open(os.path.join(ROOT, 'bots.json'), 'w'), indent=2, ensure_ascii=False)
with open(os.path.join(ROOT, 'bots.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['handle', 'user_id', 'post_id', 'post_url', 'created_at_utc', 'evidence_html'])
    for o in out: w.writerow([o['handle'], o['user_id'], o['post_id'], o['post_url'], o['created_at_utc'], o['evidence_html']])
ok = sum(1 for l in log if l[2] == 'oembed_ok')
print(f'DONE accounts={len(rows)} oembed_ok={ok} reconstructed={len(log)-ok}')
