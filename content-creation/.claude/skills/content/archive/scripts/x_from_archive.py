"""
Imports the owner's X posts from the official X data export (data/tweets.js)
into the content archive.

Usage:
    python x_from_archive.py <path/to/tweets.js> <archive_root> [cutoff YYYY-MM-DD] [handle]

Keeps original posts and threads. A thread is a post plus his own replies
chained under it; the chain is saved as one file. Replies to other people and
reposts ("RT @...") are skipped. [handle] is only used to build URLs; without
it, URLs use x.com/i/web/status/<id>. Skips files that already exist.
"""

import json
import os
import re
import sys
from datetime import datetime

CUTOFF_DEFAULT = "2024-01-01"


def load_tweets(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    raw = raw[raw.index("["):]  # strip "window.YTD.tweets.part0 = "
    return [entry.get("tweet", entry) for entry in json.loads(raw)]


def week_path(date):
    week = min((date.day - 1) // 7 + 1, 4)
    return date.strftime("%Y"), date.strftime("%m"), "WEEK {:02d}".format(week)


def slugify(text, n_words=8):
    text = re.sub(r"https?://\S+", "", text)
    slug = "-".join(text.strip().split()[:n_words]).lower()
    slug = re.sub(r"[^\w\-]", "", slug)
    return re.sub(r"-+", "-", slug).strip("-")[:60] or "post"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tweets_js, root = sys.argv[1], sys.argv[2]
    cutoff = datetime.strptime(sys.argv[3] if len(sys.argv) > 3 else CUTOFF_DEFAULT, "%Y-%m-%d")
    handle = sys.argv[4].lstrip("@") if len(sys.argv) > 4 else None

    tweets = load_tweets(tweets_js)
    by_id = {t["id_str"]: t for t in tweets}
    children = {}
    for t in tweets:
        parent = t.get("in_reply_to_status_id_str")
        if parent in by_id:
            children.setdefault(parent, []).append(t)

    counts = {"created": 0, "exists": 0, "skipped": 0, "cutoff": 0}
    for t in tweets:
        text = t.get("full_text", "")
        parent = t.get("in_reply_to_status_id_str")
        if text.startswith("RT @") or (parent and parent in by_id):
            continue  # repost, or a continuation that gets saved with its root
        if parent:
            counts["skipped"] += 1  # reply to someone else
            continue

        date = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y").replace(tzinfo=None)
        if date < cutoff:
            counts["cutoff"] += 1
            continue

        chain, node = [t], t
        while children.get(node["id_str"]):
            node = sorted(children[node["id_str"]], key=lambda c: c["id_str"])[0]
            chain.append(node)

        year, month, week = week_path(date)
        folder = os.path.join(root, year, month, week, "x")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "{}-{}.md".format(date.strftime("%Y-%m-%d"), slugify(text)))
        if os.path.exists(path):
            counts["exists"] += 1
            continue

        base = "https://x.com/{}/status/".format(handle) if handle else "https://x.com/i/web/status/"
        title = " ".join(text.split()[:10]).replace('"', '\\"')
        body = "\n\n[thread continues]\n\n".join(c.get("full_text", "") for c in chain)
        kind = "thread ({} posts)".format(len(chain)) if len(chain) > 1 else "post"
        with open(path, "w", encoding="utf-8") as f:
            f.write('---\ntitle: "{}"\ndate: {}\nplatform: x\nurl: {}{}\npipeline_id:\nkind: {}\n---\n\n{}\n'
                    .format(title, date.strftime("%Y-%m-%d"), base, t["id_str"], kind, body))
        counts["created"] += 1

    print("created {created} | already archived {exists} | replies to others skipped {skipped} | "
          "pre-cutoff {cutoff}".format(**counts))


if __name__ == "__main__":
    main()
