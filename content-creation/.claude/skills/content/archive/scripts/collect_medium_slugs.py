"""
Pages the Medium public profile API for one author and writes every
article slug + publish date (after a cutoff) to a JSON file. No auth needed.
The Medium user id is in context/accounts.md.

Usage:
    python collect_medium_slugs.py <user_id>                          # cutoff 2024-01-01, writes slugs.json
    python collect_medium_slugs.py <user_id> 2025-01-01               # custom cutoff
    python collect_medium_slugs.py <user_id> 2025-01-01 out.json      # custom cutoff and output
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://medium.com/_/api/users/{}/profile/stream"
CUTOFF_DEFAULT = "2024-01-01"


def fetch_page(user_id, cursor=None):
    url = BASE_URL.format(user_id) + "?limit=25&source=overview"
    if cursor:
        url += "&to={}".format(cursor)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
    # Medium prepends ")]}'" as CSRF protection
    if raw.startswith("])}while(1);</x>"):
        raw = raw[len("])}while(1);</x>"):]
    if raw.startswith(")]}'"):
        raw = raw[4:].lstrip()
    return json.loads(raw)


def extract_posts(data):
    posts = []
    post_refs = data.get("payload", {}).get("references", {}).get("Post", {})
    for post in post_refs.values():
        slug = post.get("uniqueSlug", "")
        published_ms = post.get("firstPublishedAt", 0)
        if slug and published_ms:
            posts.append({
                "slug": slug,
                "title": post.get("title", ""),
                "publishedAt": published_ms,
                "date": datetime.fromtimestamp(published_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
            })
    return posts


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    user_id = sys.argv[1]
    cutoff_str = sys.argv[2] if len(sys.argv) > 2 else CUTOFF_DEFAULT
    out_file = sys.argv[3] if len(sys.argv) > 3 else "slugs.json"
    cutoff = datetime.strptime(cutoff_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    all_slugs = {}
    cursor = None
    page = 0
    while True:
        page += 1
        data = fetch_page(user_id, cursor)
        posts = extract_posts(data)
        new = 0
        for p in posts:
            if p["slug"] not in all_slugs:
                all_slugs[p["slug"]] = p
                new += 1
        print("page {}: {} posts, {} new, {} unique".format(page, len(posts), new, len(all_slugs)))
        cursor = data.get("payload", {}).get("paging", {}).get("to")
        if not cursor:
            break

    cutoff_ms = cutoff.timestamp() * 1000
    kept = sorted((v for v in all_slugs.values() if v["publishedAt"] >= cutoff_ms),
                  key=lambda x: x["publishedAt"])

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)

    print("unique slugs: {} | after cutoff {}: {} | written to {}".format(
        len(all_slugs), cutoff_str, len(kept), out_file))


if __name__ == "__main__":
    main()
