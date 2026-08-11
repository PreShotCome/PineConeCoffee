# The Pinecone Coffee

The website for The Pinecone Coffee — thepineconecoffee.com — served as a static
site from GitHub Pages.

**The Pinecone Coffee is a concept brand**, built as a design and build showcase
by [Techne](https://dokazindustries.com/techne/). It is not a trading business.
That constraint shapes the markup, and it matters:

- there is **no street address and no geo coordinate** anywhere in the page or the
  structured data, only a locality (Puyallup, WA). Publishing an invented address
  would put a false place into search indexes and AI answers.
- the telephone number is inside the `555-01xx` range, which is permanently
  reserved for fictional use.
- there is **no `aggregateRating`, no `review`, and no `sameAs`** — no invented
  ratings, and no links to social profiles that do not exist.

If the brand ever becomes a real shop, put the real details in `tools/content.py`,
delete the `concept_note` and the footer disclosure in `tools/build.py`, and
rebuild.

## How it is built

Every page is plain, static, **zero-JavaScript** HTML. There is no framework and
no runtime. The pages are generated so that the visible copy and the JSON-LD
structured data come from one source and cannot drift apart — search engines
discount structured data describing things a visitor cannot see.

```
tools/content.py   the menu, hours, FAQ, business facts — edit this
tools/build.py     renders every page + sitemap.xml + robots.txt
tools/validate.py  static checks (run before every commit)
tools/check_responsive.py   headless overflow check at phone widths
```

Rebuild after any content change:

```sh
cd tools && python build.py
```

Do not hand-edit `index.html`, `about/`, `menu/`, `hours/`, `404.html`,
`sitemap.xml`, `robots.txt` or `site.webmanifest` — they are generated and your
edits will be overwritten. `assets/css/site.css` **is** hand-maintained.

## Checks

```sh
python tools/validate.py                 # no browser needed

python -m http.server 8791 --bind 127.0.0.1   # in another shell
python tools/check_responsive.py
```

`validate.py` enforces the things that are easy to break and hard to notice:
tag balance, UTF-8 with no mojibake, zero executable script, no inline
`style`/`on*` attributes (the CSP forbids both), alt text and intrinsic
dimensions on every image, exactly one `<h1>`, canonical/description/OG/Twitter
tags, that every local link and `srcset` entry resolves, that the JSON-LD parses
and its `@id` references resolve, that no fabricated rating or address has crept
in, and that **every price and item name on the menu page also appears in the
structured data**.

## Notes

- Fonts (Cinzel, Lora) are self-hosted variable `woff2`, ~108 KB for all weights
  and both styles. No third-party requests are made from any page.
- Photography is self-hosted and pre-sized: AVIF, WebP and JPEG at several
  widths, chosen with `srcset`/`sizes`.
- The Content-Security-Policy is `default-src 'none'` with `script-src 'none'`.
  It is delivered as a `<meta>` tag because GitHub Pages cannot set headers;
  for that reason `frame-ancestors` is declared but not enforced.
- Canonical host is `https://www.thepineconecoffee.com/`. The apex 301-redirects
  to `www`, per the `CNAME` file.
