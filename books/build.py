#!/usr/bin/env python3
"""Copy free public-domain books from Project Gutenberg into this site.

Browsers can't download book text straight from gutenberg.org (no CORS),
so this script saves cleaned plain-text copies under books/<id>.txt and
writes books/catalog.json for the shelves. Run by the "Fetch books"
GitHub Action; you can also run it locally: python3 books/build.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "BOOKOUT-library-builder/1.0 (+https://github.com/YushAbdullah/BOOKOUT)"}
TOPICS = {
    "adventure": "adventure", "mystery": "detective", "romance": "love stories",
    "scifi": "science fiction", "fantasy": "fantasy", "horror": "horror",
    "poetry": "poetry", "philosophy": "philosophy", "history": "history",
    "children": "children", "humor": "humor", "growth": "conduct of life",
    "inspiration": "success", "business": "business", "innovation": "inventions", "leadership": "leadership",
    "people": "conduct of life", "finance": "finance", "ops": "industrial management", "sales": "advertising",
}
PER_CAT = int(os.environ.get("BOOKS_PER_CATEGORY", "10"))  # shelf size per category
MAX_BYTES = 2_600_000  # skip giant books to keep the site light
DEADLINE = time.time() + int(os.environ.get("BOOKS_TIME_BUDGET", "1500"))  # stop early and save what we have; next run continues


def get(url, tries=2, timeout=30):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i + 1} {url}: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def clean(text):
    text = text.replace("\r", "").lstrip("﻿")
    s = re.search(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\n", text, re.I)
    if s:
        text = text[s.end():]
    e = re.search(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", text, re.I)
    if e:
        text = text[:e.start()]
    return text.strip() + "\n"


def name(a):
    return " ".join(reversed(a.get("name", "").split(", "))) if a else "Unknown"


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def resolve(picks):
    """Check hand-picked IDs against Gutendex and look up picks given only as "find": "Title|Author"."""
    ids = sorted({b["id"] for s in picks.values() for b in s if b.get("id")})
    known = {}
    for i in range(0, len(ids), 30):
        raw = get("https://gutendex.com/books/?" + urllib.parse.urlencode({"ids": ",".join(map(str, ids[i:i + 30]))}), tries=1, timeout=25)
        for b in (json.loads(raw).get("results", []) if raw else []):
            known[b["id"]] = b

    def search(title, author=""):
        raw = get("https://gutendex.com/books/?" + urllib.parse.urlencode({"search": f"{title} {author}".strip(), "languages": "en"}), tries=1, timeout=25)
        for b in (json.loads(raw).get("results", []) if raw else []):
            if not b.get("copyright") and norm(title)[:18] in norm(b["title"]):
                return b
        return None

    out = {}
    for cat, shelf in picks.items():
        keep = []
        for b in shelf:
            if b.get("find"):
                title, _, author = b["find"].partition("|")
                hit = search(title, author)
                if not hit:
                    print(f"  could not find {b['find']}")
                    continue
                b = {"id": hit["id"], "title": title.strip(), "author": ", ".join(name(a) for a in hit.get("authors", [])) or author}
            elif known and b["id"] in known and norm(b["title"]).replace(" ", "")[:8] not in norm(known[b["id"]]["title"]).replace(" ", ""):
                hit = search(b["title"], b["author"])
                print(f"  id {b['id']} is not {b['title']!r}; " + (f"using {hit['id']}" if hit else "dropping it"))
                if not hit:
                    continue
                b = dict(b, id=hit["id"])
            keep.append(b)
        out[cat] = keep
    return out


def main():
    picks = resolve(json.load(open(os.path.join(HERE, "picks.json")))) if time.time() < DEADLINE - 900 else json.load(open(os.path.join(HERE, "picks.json")))
    catalog = {}
    # hand-picked books first, so they are saved even if the catalogue server is slow
    for cat, topic in TOPICS.items():
        shelf = []
        for b in picks.get(cat, []):
            if b.get("id") and b["id"] not in {x["id"] for x in shelf}:
                shelf.append(b)
        seen = {b["id"] for b in shelf}
        q = urllib.parse.urlencode({"topic": topic, "languages": "en", "mime_type": "text/plain"})
        raw = get(f"https://gutendex.com/books/?{q}", tries=1, timeout=25) if time.time() < DEADLINE - 600 else None
        for b in (json.loads(raw).get("results", []) if raw else []):
            if len(shelf) >= PER_CAT:
                break
            if b["id"] in seen or b.get("copyright"):
                continue
            title = re.sub(r"\s*[:;]\s*$", "", b["title"].split("\r")[0].split("\n")[0])
            shelf.append({"id": b["id"], "title": title, "author": ", ".join(name(a) for a in b.get("authors", [])) or "Unknown"})
            seen.add(b["id"])
        catalog[cat] = shelf
        print(f"{cat}: {len(shelf)} books")

    ok = set()
    pick_ids = [b["id"] for s in picks.values() for b in s if b.get("id")]
    order = list(dict.fromkeys(pick_ids + [b["id"] for s in catalog.values() for b in s]))
    for bid in order:
        path = os.path.join(HERE, f"{bid}.txt")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            ok.add(bid)
            continue
        if time.time() > DEADLINE:
            print("  time budget used up; the next run will fetch the rest")
            break
        data = get(f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt")
        time.sleep(1)  # be polite to Project Gutenberg
        if not data:
            print(f"  skip {bid}: download failed")
            continue
        text = clean(data.decode("utf-8", "replace"))
        if len(text.encode()) > MAX_BYTES:
            print(f"  skip {bid}: too large")
            continue
        open(path, "w", encoding="utf-8").write(text)
        ok.add(bid)
        print(f"  saved {bid}")

    catalog = {c: [b for b in s if b["id"] in ok] for c, s in catalog.items()}
    json.dump({"generated": time.strftime("%Y-%m-%d"), "cats": catalog}, open(os.path.join(HERE, "catalog.json"), "w"), indent=1, ensure_ascii=False)
    print(f"catalog: {len(ok)} books")


if __name__ == "__main__":
    main()
