"""Openly licensed reading that is not on Project Gutenberg.

* AI books: Microsoft's "AI for Beginners" and "ML for Beginners" curricula
  (MIT licence), stitched from their lesson pages into two readable books.
* Articles: Wikipedia articles (CC BY-SA 4.0), saved as plain text with the
  lead image as the cover and a credit line on the first page.

Called from build.py. Every item gets books/<id>.txt and a catalog entry with
src "open", so the app reads it from the site like the Gutenberg books.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "BOOKOUT-library-builder/1.0 (+https://github.com/YushAbdullah/BOOKOUT)"}
RAW = "https://raw.githubusercontent.com/microsoft/{repo}/main/{path}"

MS_BOOKS = [
    {
        "id": "ms-ai-beginners", "repo": "AI-For-Beginners", "title": "Artificial Intelligence for Beginners",
        "author": "Microsoft Cloud Advocates", "cover": "lessons/sketchnotes/ai-overview.png", "cats": ["ai", "innovation"], "aud": ["education", "teens"],
        "lessons": ["lessons/1-Intro/README.md", "lessons/2-Symbolic/README.md", "lessons/3-NeuralNetworks/README.md",
                    "lessons/3-NeuralNetworks/03-Perceptron/README.md", "lessons/4-ComputerVision/06-IntroCV/README.md",
                    "lessons/5-NLP/README.md", "lessons/5-NLP/13-TextRep/README.md", "lessons/5-NLP/18-Transformers/README.md",
                    "lessons/5-NLP/20-LangModels/README.md", "lessons/6-Other/23-MultiagentSystems/README.md", "lessons/7-Ethics/README.md"],
    },
    {
        "id": "ms-ml-beginners", "repo": "ML-For-Beginners", "title": "Machine Learning for Beginners",
        "author": "Microsoft Cloud Advocates", "cover": "images/ml-for-beginners.png", "cats": ["ai"], "aud": ["education", "teens"],
        "lessons": ["1-Introduction/1-intro-to-ML/README.md", "1-Introduction/2-history-of-ML/README.md", "1-Introduction/3-fairness/README.md",
                    "1-Introduction/4-techniques-of-ML/README.md", "4-Classification/1-Introduction/README.md", "5-Clustering/1-Visualize/README.md",
                    "6-NLP/1-Introduction-to-NLP/README.md", "8-Reinforcement/1-QLearning/README.md", "9-Real-World/1-Applications/README.md"],
    },
]

# Wikipedia articles: (title, categories, audiences)
ARTICLES = [
    ("Artificial intelligence", ["ai"], ["education", "general"]),
    ("History of artificial intelligence", ["ai", "worldhistory"], ["education", "general"]),
    ("Machine learning", ["ai"], ["education", "general"]),
    ("Large language model", ["ai"], ["education", "general"]),
    ("Turing test", ["ai"], ["education", "teens"]),
    ("Ethics of artificial intelligence", ["ai"], ["education", "general"]),
    ("Geography of Malaysia", ["geography"], ["education", "general"]),
    ("Mount Kinabalu", ["geography"], ["education", "children"]),
    ("Strait of Malacca", ["geography"], ["education", "general"]),
    ("Borneo", ["geography"], ["education", "general"]),
    ("Amazon rainforest", ["geography"], ["education", "children"]),
    ("Himalayas", ["geography"], ["education", "general"]),
    ("Sahara", ["geography"], ["education", "children"]),
    ("Nasi lemak", ["cooking"], ["general"]),
    ("Malaysian cuisine", ["cooking"], ["general"]),
    ("Rendang", ["cooking"], ["general"]),
    ("Roti canai", ["cooking"], ["general"]),
    ("Teh tarik", ["cooking"], ["general"]),
    ("Malacca Sultanate", ["worldhistory"], ["education", "general"]),
    ("Silk Road", ["worldhistory"], ["education", "general"]),
    ("Ancient Egypt", ["worldhistory"], ["education", "children"]),
    ("Industrial Revolution", ["worldhistory"], ["education", "general"]),
    ("Renaissance", ["worldhistory"], ["education", "general"]),
    ("Ibn Battuta", ["worldhistory", "inspiration", "geography"], ["education", "general"]),
    ("Tunku Abdul Rahman", ["worldhistory", "inspiration"], ["education", "general"]),
    ("Marie Curie", ["inspiration"], ["education", "teens"]),
    ("Malala Yousafzai", ["inspiration"], ["teens", "general"]),
    ("Helen Keller", ["inspiration"], ["children", "general"]),
    ("Habit", ["motivation"], ["general"]),
    ("Grit (personality trait)", ["motivation"], ["general"]),
    ("Kaizen", ["motivation"], ["general"]),
    ("Pomodoro Technique", ["motivation"], ["teens", "general"]),
    ("Stoicism", ["motivation", "philosophy"], ["general"]),
    ("Solar System", ["innovation"], ["children", "education"]),
    ("Dinosaur", ["children"], ["children", "education"]),
    ("Water cycle", ["geography"], ["children", "education"]),
    ("Photosynthesis", ["innovation"], ["children", "education"]),
]
SKIP_SECTIONS = re.compile(r"^(references|external links|see also|notes|further reading|bibliography|citations|sources|footnotes|explanatory notes|works cited|gallery)$", re.I)


def get(url, tries=2, timeout=30):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i + 1} {url}: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def inline(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)               # images
    s = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", s)  # linked images
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)           # links
    s = re.sub(r"<[^>]+>", "", s)                            # html
    s = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: m.group(1) or m.group(2), s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\$([^$\n]+)\$", r"\1", s)
    return re.sub(r"[ \t]+", " ", s).strip()


def md_to_text(md):
    """Lesson markdown -> plain text paragraphs the reader understands."""
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"\$\$.*?\$\$", "", md, flags=re.S)
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out, title, skipping = [], None, False
    for line in md.split("\n"):
        raw = line.rstrip()
        h = re.match(r"^(#{1,4})\s+(.*)", raw)
        if h:
            text = inline(h.group(2))
            if re.search(r"quiz|assignment|^\W*$", text, re.I):
                skipping = bool(re.search(r"assignment|post-lecture", text, re.I))
                continue
            skipping = False
            if len(h.group(1)) == 1 and title is None:
                title = text
                continue
            out += ["", re.sub(r"[^\w\s'&,:-]", "", text).strip().upper(), ""]
            continue
        if skipping:
            continue
        s = raw.strip()
        if re.match(r"^(---+|\*\*\*+)$", s) or re.search(r"quiz|click the image|sketchnote by|photo by|image by|🎥|youtu", s, re.I):
            out.append("")
            continue
        if re.match(r"^\|?\s*:?-{3,}", s):
            continue
        if "|" in s and s.count("|") >= 1 and not s.startswith(">"):
            cells = [inline(c) for c in s.strip("|").split("|")]
            s = " — ".join(c for c in cells if c)
            out += ["", s, ""]
            continue
        s = re.sub(r"^>\s?", "", s)
        li = re.match(r"^(\s*)([*+-]|\d+\.)\s+(.*)", raw)
        if li:
            out += ["", "• " + inline(li.group(3)), ""]
            continue
        s = inline(s)
        if re.search(r"quiz|click the image|sketchnote by|photo by|image by|🎥|youtu|^(photo|image) \w", s, re.I):
            out.append("")
            continue
        out.append(s)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text


def build_ms(catalog, ok):
    for bk in MS_BOOKS:
        path = os.path.join(HERE, f"{bk['id']}.txt")
        if not (os.path.exists(path) and os.path.getsize(path) > 5000):
            parts = [f"{bk['title'].upper()}", "",
                     f"By {bk['author']}. Lessons from the free \"{bk['repo'].replace('-', ' ')}\" curriculum, "
                     f"published by Microsoft under the MIT licence at github.com/microsoft/{bk['repo']}. "
                     "Code samples, quizzes and pictures are left out so the lessons read like a book.", ""]
            n = 0
            for p in bk["lessons"]:
                raw = get(RAW.format(repo=bk["repo"], path=p))
                if not raw:
                    print(f"  skip lesson {p}")
                    continue
                title, text = md_to_text(raw.decode("utf-8", "replace"))
                if len(text) < 400:
                    continue
                n += 1
                parts += ["", f"CHAPTER {n}. {title or p.split('/')[-2]}", "", text, ""]
            if n < 3:
                print(f"  skip {bk['id']}: only {n} lessons")
                continue
            open(path, "w", encoding="utf-8").write("\n".join(parts).strip() + "\n")
            print(f"  saved {bk['id']} ({n} chapters)")
        entry = {"id": bk["id"], "title": bk["title"], "author": bk["author"], "src": "open", "kind": "book", "aud": bk["aud"],
                 "cover": RAW.format(repo=bk["repo"], path=bk["cover"]), "page": f"https://github.com/microsoft/{bk['repo']}", "lic": "MIT licence"}
        ok.add(bk["id"])
        for c in bk["cats"]:
            catalog.setdefault(c, []).insert(0, entry)


def wiki_text(extract):
    """Wikipedia plain extract (== Heading == style) -> reader text without reference sections."""
    out, skip = [], False
    for line in extract.split("\n"):
        m = re.match(r"^(=+)\s*(.*?)\s*=+$", line.strip())
        if m:
            name = m.group(2)
            if len(m.group(1)) == 2:
                skip = bool(SKIP_SECTIONS.match(name))
            if not skip:
                out += ["", name.upper(), ""]
            continue
        if not skip:
            out.append(line.strip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def build_articles(catalog, ok, deadline):
    for title, cats, aud in ARTICLES:
        aid = "w-" + slug(title)
        path, meta_path = os.path.join(HERE, f"{aid}.txt"), os.path.join(HERE, "articles.json")
        meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        if not (os.path.exists(path) and aid in meta):
            if time.time() > deadline:
                print("  time budget used up; articles continue next run")
                break
            q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "titles": title,
                                        "prop": "extracts|pageimages|info", "explaintext": 1, "exsectionformat": "wiki",
                                        "piprop": "thumbnail", "pithumbsize": 480, "inprop": "url"})
            raw = get("https://en.wikipedia.org/w/api.php?" + q)
            time.sleep(0.5)
            pages = list((json.loads(raw).get("query", {}).get("pages", {}) if raw else {}).values())
            if not pages or "extract" not in pages[0] or len(pages[0]["extract"]) < 1500:
                print(f"  skip article {title}")
                continue
            p = pages[0]
            url = p.get("fullurl") or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
            body = wiki_text(p["extract"])
            head = (f"{p.get('title', title).upper()}\n\nFrom Wikipedia, the free encyclopedia. Text by Wikipedia contributors, "
                    f"shared under the Creative Commons Attribution-ShareAlike 4.0 licence (CC BY-SA 4.0). Source and full history: {url}\n\n")
            open(path, "w", encoding="utf-8").write(head + body + "\n")
            meta[aid] = {"title": p.get("title", title), "page": url, "cover": (p.get("thumbnail") or {}).get("source", "")}
            json.dump(meta, open(meta_path, "w"), indent=1, ensure_ascii=False)
            print(f"  saved {aid}")
        m = meta[aid]
        entry = {"id": aid, "title": m["title"], "author": "Wikipedia contributors", "src": "open", "kind": "article", "aud": aud,
                 "cover": m.get("cover", ""), "page": m["page"], "lic": "CC BY-SA 4.0"}
        ok.add(aid)
        catalog.setdefault("articles", []).append(entry)
        for c in cats:
            catalog.setdefault(c, []).append(entry)


def build(catalog, ok, deadline):
    build_ms(catalog, ok)
    build_articles(catalog, ok, deadline)
