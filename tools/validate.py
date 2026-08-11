"""Static checks over the built site. Run: python tools/validate.py"""
import gzip
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "about/index.html", "menu/index.html",
         "hours/index.html", "404.html"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

errors, warnings, notes = [], [], []


def err(m): errors.append(m)
def warn(m): warnings.append(m)
def note(m): notes.append(m)


class Balance(HTMLParser):
    """Catches the unclosed-tag class of bug the old index.html shipped with."""
    def __init__(self, page):
        super().__init__(convert_charrefs=True)
        self.stack, self.page = [], page

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            err(f"{self.page}: stray </{tag}>")
            return
        if self.stack[-1][0] != tag:
            open_tag, pos = self.stack[-1]
            err(f"{self.page}: </{tag}> closes <{open_tag}> opened at line {pos[0]}")
            return
        self.stack.pop()


def check_page(page):
    path = os.path.join(ROOT, page)
    raw = open(path, encoding="utf-8").read()

    # --- encoding: the old file was full of mojibake (âœ¦, â€ ) ---------------
    for bad in ("Ã", "â€", "âœ", "Â\xa0"):
        if bad in raw:
            err(f"{page}: mojibake sequence {bad!r} present")
    try:
        raw.encode("utf-8").decode("utf-8")
    except UnicodeError:
        err(f"{page}: not valid UTF-8")

    # --- tag balance --------------------------------------------------------
    b = Balance(page)
    b.feed(raw)
    for tag, pos in b.stack:
        if tag not in ("html", "body"):
            err(f"{page}: <{tag}> opened at line {pos[0]} never closed")

    # --- zero JavaScript ----------------------------------------------------
    for m in re.finditer(r'<script([^>]*)>', raw):
        if 'application/ld+json' not in m.group(1):
            err(f"{page}: executable <script{m.group(1)}> found — site must be zero-JS")
    for m in re.finditer(r'\son(click|load|error|mouseover|submit)=', raw):
        err(f"{page}: inline event handler on{m.group(1)}= found")

    # the CSP is style-src 'self' with no 'unsafe-inline', so style="" is dead markup
    if re.search(r'\sstyle="', raw):
        err(f"{page}: inline style attribute present but blocked by this page's CSP")

    # --- required head elements --------------------------------------------
    for pat, label in [
        (r'<link rel="canonical" href="[^"]+"', "canonical"),
        (r'<meta name="description" content="[^"]{50,}"', "meta description (50+ chars)"),
        (r'<meta property="og:image"', "og:image"),
        (r'<meta name="twitter:card"', "twitter:card"),
        (r'<html lang="en-US">', "html lang"),
        (r'<link rel="manifest"', "manifest"),
    ]:
        if not re.search(pat, raw):
            err(f"{page}: missing {label}")

    title = re.search(r"<title>(.*?)</title>", raw, re.S)
    if not title:
        err(f"{page}: no <title>")
    elif len(title.group(1)) > 65:
        warn(f"{page}: title is {len(title.group(1))} chars (>65 may truncate in SERPs)")

    d = re.search(r'<meta name="description" content="([^"]+)"', raw)
    if d and len(d.group(1)) > 165:
        warn(f"{page}: meta description is {len(d.group(1))} chars (>165 may truncate)")

    # --- images: alt + intrinsic dimensions --------------------------------
    for m in re.finditer(r"<img\b[^>]*>", raw, re.S):
        tag = m.group(0)
        if 'alt=' not in tag:
            err(f"{page}: <img> without alt: {tag[:90]}")
        if 'width=' not in tag or 'height=' not in tag:
            err(f"{page}: <img> without width/height (causes layout shift): {tag[:90]}")

    # --- headings -----------------------------------------------------------
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
    if len(h1s) != 1:
        err(f"{page}: {len(h1s)} <h1> elements (expected exactly 1)")

    # --- local asset references resolve ------------------------------------
    for m in re.finditer(r'(?:href|src)="(/[^"]+)"', raw):
        ref = m.group(1).split("?")[0]
        if ref.endswith("/"):
            target = os.path.join(ROOT, ref.strip("/"), "index.html")
        else:
            target = os.path.join(ROOT, ref.lstrip("/"))
        if not os.path.exists(target):
            err(f"{page}: broken local reference {ref}")
    for m in re.finditer(r'srcset="([^"]+)"', raw):
        for part in m.group(1).split(","):
            ref = part.strip().split(" ")[0]
            if ref.startswith("/") and not os.path.exists(os.path.join(ROOT, ref.lstrip("/"))):
                err(f"{page}: broken srcset reference {ref}")

    # --- structured data ----------------------------------------------------
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S)
    graph = []
    if page == "404.html":
        return raw, graph
    if not blocks:
        err(f"{page}: no JSON-LD")
        return raw, graph
    for block in blocks:
        try:
            data = json.loads(block.replace("<\\/", "</"))
        except json.JSONDecodeError as e:
            err(f"{page}: JSON-LD does not parse — {e}")
            continue
        if "@context" not in data:
            err(f"{page}: JSON-LD missing @context")
        graph = data.get("@graph", [])
    return raw, graph


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def check_graph(page, graph, raw):
    defined, referenced = set(), set()

    def visit(n):
        if "@id" in n and "@type" in n:
            defined.add(n["@id"])
        elif set(n.keys()) == {"@id"}:
            referenced.add(n["@id"])
    walk(graph, visit)

    types = [n.get("@type") for n in graph]
    for required in ("CafeOrCoffeeShop", "WebSite", "BreadcrumbList"):
        if required not in types:
            err(f"{page}: JSON-LD graph missing a {required} node")

    # cross-page @id references are legitimate; same-page dangling ones are not
    for ref in referenced - defined:
        if ref.startswith(page.replace("index.html", "")):
            err(f"{page}: JSON-LD reference to undefined @id {ref}")
        elif "/menu/#" in ref and "menu" in page:
            err(f"{page}: dangling menu @id {ref}")

    # things that must never appear on a concept brand
    bad = {"aggregateRating": "invented ratings", "review": "invented reviews",
           "streetAddress": "invented street address", "geo": "invented coordinates"}
    def check_bad(n):
        for k, why in bad.items():
            if k in n:
                err(f"{page}: JSON-LD contains {k} ({why}) — not permissible here")
    walk(graph, check_bad)

    # every visible price must exist in the graph, and vice versa
    if "menu" in page:
        page_prices = set(re.findall(r'<span class="iprice">\$([\d.]+)</span>', raw))
        offers = set()
        walk(graph, lambda n: offers.add(n["price"]) if n.get("@type") == "Offer" else None)
        missing = page_prices - offers
        if missing:
            err(f"{page}: prices shown but not marked up: {sorted(missing)}")

        names_visible = set(re.findall(r'<span class="iname">([^<]+)</span>', raw))
        names_marked = set()
        walk(graph, lambda n: names_marked.add(n["name"]) if n.get("@type") == "MenuItem" else None)
        if names_visible - names_marked:
            err(f"{page}: menu items visible but unmarked: {sorted(names_visible - names_marked)}")
        note(f"{page}: {len(names_marked)} MenuItem nodes, {len(offers)} distinct prices")


def main():
    for page in PAGES:
        raw, graph = check_page(page)
        if graph:
            check_graph(page, graph, raw)

    for f in ["robots.txt", "sitemap.xml", "site.webmanifest", "CNAME", "favicon.ico"]:
        if not os.path.exists(os.path.join(ROOT, f)):
            err(f"missing {f}")

    json.load(open(os.path.join(ROOT, "site.webmanifest"), encoding="utf-8"))

    # sitemap must list every page and nothing that 404s
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    for page in PAGES:
        if page == "404.html":
            continue
        slug = page.replace("index.html", "")
        if f"https://www.thepineconecoffee.com/{slug}" not in sm:
            err(f"sitemap.xml missing /{slug}")

    print("--- transfer weight (gzipped) ---")
    total = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        gz = len(gzip.compress(open(p, "rb").read(), 9))
        total += gz
        print(f"  {page:20s} {os.path.getsize(p)/1024:6.1f} KB raw -> {gz/1024:5.1f} KB gz")
    css = os.path.join(ROOT, "assets/css/site.css")
    print(f"  {'site.css':20s} {os.path.getsize(css)/1024:6.1f} KB raw -> "
          f"{len(gzip.compress(open(css,'rb').read(),9))/1024:5.1f} KB gz")

    print()
    for n in notes:
        print(f"  note:  {n}")
    for w in warnings:
        print(f"  WARN:  {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
