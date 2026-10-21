"""
Imports the owner's LinkedIn posts from an Apify dataset
(actor harvestapi/linkedin-profile-posts) into the content archive.

The Apify token is read from the APIFY_TOKEN environment variable. Never put
it in this file or in a saved command.

Usage:
    python linkedin_from_apify.py <dataset_id> <archive_root> <public_id> [cutoff YYYY-MM-DD]

<public_id> is the LinkedIn profile id from context/accounts.md (linkedin.com/in/<public_id>).
Keeps only posts authored by that profile (drops reshares), skips files that
already exist, never deletes anything.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime

CUTOFF_DEFAULT = "2024-01-01"


def week_path(date):
    week = min((date.day - 1) // 7 + 1, 4)
    return date.strftime("%Y"), date.strftime("%m"), "WEEK {:02d}".format(week)


def slugify(text, n_words=8):
    slug = "-".join(text.strip().split()[:n_words]).lower()
    slug = re.sub(r"[^\w\-]", "", slug)
    return re.sub(r"-+", "-", slug).strip("-")[:60]


def fetch_all(dataset_id, token):
    items, offset, limit = [], 0, 200
    while True:
        url = ("https://api.apify.com/v2/datasets/{}/items?limit={}&offset={}&format=json"
               .format(dataset_id, limit, offset))
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(req) as resp:
            batch = json.loads(resp.read())
        items.extend(batch)
        if len(batch) < limit:
            return items
        offset += limit


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    dataset_id, root, author_id = sys.argv[1], sys.argv[2], sys.argv[3]
    cutoff = datetime.strptime(sys.argv[4] if len(sys.argv) > 4 else CUTOFF_DEFAULT, "%Y-%m-%d")
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("APIFY_TOKEN is not set.")

    counts = {"created": 0, "exists": 0, "reshare": 0, "cutoff": 0, "empty": 0}
    for item in fetch_all(dataset_id, token):
        author = item.get("author") or {}
        if not isinstance(author, dict) or author.get("publicIdentifier") != author_id:
            counts["reshare"] += 1
            continue

        content = (item.get("content") or "").strip()
        posted = item.get("postedAt") or {}
        date_str = posted.get("date", "") if isinstance(posted, dict) else ""
        if not content or not date_str:
            counts["empty"] += 1
            continue

        date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        if date < cutoff:
            counts["cutoff"] += 1
            continue

        year, month, week = week_path(date)
        folder = os.path.join(root, year, month, week, "linkedin")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "{}-{}.md".format(date.strftime("%Y-%m-%d"), slugify(content)))
        if os.path.exists(path):
            counts["exists"] += 1
            continue

        title = " ".join(content.split()[:10]).replace('"', '\\"')
        article = item.get("article") or {}
        link = article.get("link", "") if isinstance(article, dict) else ""
        body = ('---\ntitle: "{}"\ndate: {}\nplatform: linkedin\nurl: {}\npipeline_id:\n---\n\n{}\n'
                .format(title, date.strftime("%Y-%m-%d"), item.get("shareLinkedinUrl", ""), content))
        if link:
            body += "\n[LINK: {}]\n".format(link)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        counts["created"] += 1

    print("created {created} | already archived {exists} | reshares/others skipped {reshare} | "
          "pre-cutoff {cutoff} | empty {empty}".format(**counts))


if __name__ == "__main__":
    main()
