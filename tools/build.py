"""
Builds every page of thepineconecoffee.com from tools/content.py.

Run:  python tools/build.py

Emits plain static HTML with zero JavaScript. The visible copy and the
JSON-LD graph are produced from the same Python objects, so they cannot
disagree with each other.
"""
import json
import os
import re

from content import (ADDONS, AMENITIES, BASE, BIZ, BUILD_DATE, DIET_LABEL,
                     FAQ, HOURS, MENU, VALUES)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- images ----
# name -> (native_w, native_h, [widths])
# Names describe what each photograph actually shows, so alt text can be
# checked against the file. Do not rename without re-checking the alt strings.
IMAGES = {
    "forest":  (2400, 1600, [640, 1024, 1600, 2048]),  # dark misty forest, ferns
    "ridge":   (2400, 1594, [640, 1024, 1600]),        # cloud over a forested hillside
    "rainier": (2400, 1350, [640, 1024, 1600]),        # mountain ridge at sunset
    "cheers":  (2400, 1600, [640, 1024, 1600]),        # hands raising lattes, overhead
    "sack":    (2400, 1600, [400, 640, 1024]),         # beans in a burlap sack
    "lattes":  (2400, 3600, [400, 800]),               # three lattes, portrait
}

ALT = {
    "forest": "A dark, misty evergreen forest, soft light falling through the trunks "
              "onto ferns and undergrowth",
    "ridge":  "Low cloud drifting across a steep hillside of dense evergreen forest",
    "rainier": "Evergreens in the foreground with a jagged mountain ridge behind them "
               "and the sun setting through the trees",
    "cheers": "Three hands seen from above, raising two lattes with leaf-patterned foam "
              "art and a glass of cold brew over a wooden table",
    "sack":   "Dark-roasted coffee beans heaped in an open burlap sack against a black "
              "background",
    "lattes": "Three lattes with rosetta and heart foam art on black saucers, on a "
              "wooden table surrounded by houseplants",
}


def srcset(name, ext):
    return ", ".join(f"/assets/img/{name}-{w}.{ext} {w}w" for w in IMAGES[name][2])


def picture(name, alt, sizes, cls="", lcp=False, img_cls=""):
    """Responsive <picture>: AVIF, then WebP, then a JPEG every browser reads."""
    nw, nh, widths = IMAGES[name]
    fallback = widths[min(1, len(widths) - 1)]
    h = round(nh * nw / nw)  # keep native ratio on the attributes
    # decoding="async" is deliberately omitted on the LCP image — it lets the
    # browser paint the frame before the hero has decoded, which delays LCP.
    loading = ('loading="eager" fetchpriority="high"' if lcp
               else 'loading="lazy" decoding="async"')
    cls_attr = f' class="{cls}"' if cls else ""
    img_cls_attr = f' class="{img_cls}"' if img_cls else ""
    return f"""<picture{cls_attr}>
      <source type="image/avif" srcset="{srcset(name, 'avif')}" sizes="{sizes}">
      <source type="image/webp" srcset="{srcset(name, 'webp')}" sizes="{sizes}">
      <img{img_cls_attr} src="/assets/img/{name}-{fallback}.jpg" srcset="{srcset(name, 'jpg')}"
           sizes="{sizes}" width="{nw}" height="{nh}" alt="{alt}" {loading}>
    </picture>"""


# ------------------------------------------------------------------ chrome --
NAV_ITEMS = [("about/", "About"), ("menu/", "Menu"), ("hours/", "Hours")]


def url(path):
    return f"{BASE}/{path}" if path else f"{BASE}/"


def nav(current):
    links = []
    for path, label in NAV_ITEMS:
        cur = ' aria-current="page"' if path == current else ""
        links.append(f'<li><a href="/{path}"{cur}>{label}</a></li>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<nav aria-label="Primary">
  <a class="nav-brand" href="/">The Pinecone</a>
  <ul class="nav-links">
    {chr(10).join('    ' + x for x in links).strip()}
  </ul>
</nav>"""


def footer():
    return f"""<footer class="site-footer">
  <p class="footer-brand">{BIZ['name']}</p>
  <p class="footer-line">
    <a href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a>
    &nbsp;&middot;&nbsp;
    <a href="mailto:{BIZ['email']}">{BIZ['email']}</a>
  </p>
  <ul class="footer-nav">
    <li><a href="/">Home</a></li>
    <li><a href="/about/">About</a></li>
    <li><a href="/menu/">Menu</a></li>
    <li><a href="/hours/">Hours &amp; Location</a></li>
  </ul>
  <p class="fine">{BIZ['locality']}, {BIZ['region']} &middot; Est. {BIZ['founded']} &middot; thepineconecoffee.com</p>
  <p class="note">
    The Pinecone Coffee is a concept brand &mdash; a design and build showcase by
    <a href="https://dokazindustries.com/techne/">Techne</a>, part of Dokaz Industries.
    The location and telephone number shown are illustrative.
  </p>
</footer>"""


def head(title, desc, path, og_image="og-card.jpg", extra_preload=""):
    canonical = url(path)
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">

<!-- No JavaScript is served anywhere on this site, so scripts are refused outright. -->
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self'; font-src 'self'; form-action 'none'; base-uri 'self'; frame-ancestors 'none'; script-src 'none'; object-src 'none'">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="referrer" content="strict-origin-when-cross-origin">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{BIZ['name']}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/assets/img/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Pinecone Coffee crest on a dark, misty forest">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}/assets/img/{og_image}">

<meta name="theme-color" content="#111f10">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<link rel="preload" href="/assets/fonts/cinzel-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/lora-latin-var.woff2" as="font" type="font/woff2" crossorigin>
{extra_preload}<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>"""


# ------------------------------------------------------------- structured ---
def biz_node(on_menu_page=False):
    hours_spec = [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": [f"https://schema.org/{d}" for d in days],
        "opens": opens,
        "closes": closes,
    } for days, opens, closes, _, _ in HOURS]

    node = {
        "@type": "CafeOrCoffeeShop",
        "@id": f"{BASE}/#business",
        "name": BIZ["name"],
        "alternateName": BIZ["short"],
        "url": f"{BASE}/",
        "slogan": BIZ["slogan"],
        "description": BIZ["description"],
        "disambiguatingDescription": BIZ["concept_note"],
        "foundingDate": BIZ["founded"],
        "logo": {"@id": f"{BASE}/#logo"},
        "image": {"@id": f"{BASE}/#logo"},
        "telephone": BIZ["phone_e164"],
        "email": BIZ["email"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": BIZ["locality"],
            "addressRegion": BIZ["region"],
            "postalCode": BIZ["postal"],
            "addressCountry": BIZ["country"],
        },
        "areaServed": [
            {"@type": "City", "name": "Puyallup", "sameAs": "https://en.wikipedia.org/wiki/Puyallup,_Washington"},
            {"@type": "AdministrativeArea", "name": "Pierce County, Washington"},
        ],
        "hasMap": BIZ["map_url"],
        "openingHoursSpecification": hours_spec,
        "priceRange": BIZ["price_range"],
        "currenciesAccepted": "USD",
        "paymentAccepted": "Cash, Credit Card, Debit Card, Apple Pay, Google Pay",
        "servesCuisine": ["Coffee", "Espresso", "Tea", "Pastries"],
        "knowsLanguage": "en-US",
        "publicAccess": True,
        "smokingAllowed": False,
        "isAccessibleForFree": True,
        "amenityFeature": [{
            "@type": "LocationFeatureSpecification",
            "name": name,
            "value": value,
        } for name, value in AMENITIES],
        "hasMenu": {"@id": f"{BASE}/menu/#menu"} if on_menu_page else f"{BASE}/menu/",
    }
    return node


def logo_node():
    return {
        "@type": "ImageObject",
        "@id": f"{BASE}/#logo",
        "url": f"{BASE}/assets/img/logo-420.png",
        "contentUrl": f"{BASE}/assets/img/logo-420.png",
        "width": 420,
        "height": 410,
        "caption": "The Pinecone Coffee crest: a crescent moon, a pinecone and ferns in gold and cream",
    }


def website_node():
    return {
        "@type": "WebSite",
        "@id": f"{BASE}/#website",
        "url": f"{BASE}/",
        "name": BIZ["name"],
        "description": BIZ["description"],
        "inLanguage": "en-US",
        "publisher": {"@id": f"{BASE}/#business"},
        "copyrightYear": BIZ["founded"],
        "copyrightHolder": {"@id": f"{BASE}/#business"},
    }


def breadcrumb_node(path, label):
    items = [{
        "@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/",
    }]
    if path:
        items.append({"@type": "ListItem", "position": 2, "name": label, "item": url(path)})
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url(path)}#breadcrumb",
        "itemListElement": items,
    }


def page_node(path, name, desc, image, page_type="WebPage", extra=None):
    node = {
        "@type": page_type,
        "@id": f"{url(path)}#webpage",
        "url": url(path),
        "name": name,
        "description": desc,
        "isPartOf": {"@id": f"{BASE}/#website"},
        "about": {"@id": f"{BASE}/#business"},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": f"{BASE}/assets/img/{image}-1600.jpg",
        },
        "breadcrumb": {"@id": f"{url(path)}#breadcrumb"},
        "inLanguage": "en-US",
        "datePublished": "2026-05-04",
        "dateModified": BUILD_DATE,
    }
    if extra:
        node.update(extra)
    return node


def menu_node():
    addon_ids = [{"@id": f"{BASE}/menu/#item-{slug}"} for slug, *_ in ADDONS]
    sections = []
    for section in MENU:
        items = []
        for slug, name, price, desc, badge, diets in section["items"]:
            item = {
                "@type": "MenuItem",
                "@id": f"{BASE}/menu/#item-{slug}",
                "name": name,
                "description": desc,
                "offers": {
                    "@type": "Offer",
                    "price": price,
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "seller": {"@id": f"{BASE}/#business"},
                },
            }
            if diets:
                item["suitableForDiet"] = diets if len(diets) > 1 else diets[0]
            if badge:
                item["additionalProperty"] = {
                    "@type": "PropertyValue", "name": "Availability", "value": badge,
                }
            # every drink can be customised from the add-on list
            if section["slug"] in ("espresso", "signature", "seasonal"):
                item["menuAddOn"] = addon_ids
            items.append(item)
        sections.append({
            "@type": "MenuSection",
            "@id": f"{BASE}/menu/#section-{section['slug']}",
            "name": section["name"],
            "description": section["blurb"],
            "hasMenuItem": items,
        })

    sections.append({
        "@type": "MenuSection",
        "@id": f"{BASE}/menu/#section-addons",
        "name": "Make it yours",
        "description": "Additions and swaps available on any drink.",
        "hasMenuItem": [{
            "@type": "MenuItem",
            "@id": f"{BASE}/menu/#item-{slug}",
            "name": name,
            "description": desc,
            "offers": {
                "@type": "Offer", "price": price, "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "seller": {"@id": f"{BASE}/#business"},
            },
        } for slug, name, price, desc in ADDONS],
    })

    return {
        "@type": "Menu",
        "@id": f"{BASE}/menu/#menu",
        "name": "The Pinecone Coffee menu",
        "description": "Espresso, signature and cold drinks, seasonal specials and bites.",
        "inLanguage": "en-US",
        "dateModified": BUILD_DATE,
        "hasMenuSection": sections,
    }


def faq_node():
    return {
        "@type": "FAQPage",
        "@id": f"{BASE}/hours/#faq",
        "mainEntity": [{
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        } for q, a in FAQ],
    }


def jsonld(graph):
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph},
                         indent=2, ensure_ascii=False)
    # never let a literal </script> escape from inside the JSON
    payload = payload.replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{payload}\n</script>'


# ---------------------------------------------------------------- fireflies --
# Hand-authored so the signature effect survives without JavaScript.
FF = [
    (7, 18, 9.4, 1.2, 22, -44), (19, 71, 12.1, 4.8, -18, -52), (28, 34, 6.8, 2.1, 14, -38),
    (35, 88, 10.6, 6.4, -26, -47), (41, 12, 8.2, 0.6, 30, -35), (48, 57, 13.5, 3.3, -12, -60),
    (55, 26, 7.5, 5.9, 25, -41), (61, 80, 11.2, 1.9, -22, -49), (68, 43, 9.0, 7.2, 18, -36),
    (74, 15, 12.8, 2.7, -30, -55), (81, 66, 6.4, 4.1, 12, -33), (86, 92, 10.1, 0.9, -16, -46),
    (12, 52, 11.7, 5.2, 28, -58), (23, 5, 8.6, 3.8, -20, -40), (44, 74, 13.0, 7.8, 16, -51),
    (59, 96, 7.1, 1.5, -24, -37), (70, 30, 9.8, 6.0, 20, -43), (92, 48, 12.4, 2.4, -14, -54),
    (3, 83, 8.0, 4.5, 26, -39), (37, 61, 10.9, 7.5, -28, -57),
]


def fireflies():
    # Positions come from .ff:nth-child() rules in site.css — keeping them out of
    # style="" attributes is what lets the CSP stay at style-src 'self'.
    spans = []
    for i in range(len(FF)):
        big = " big" if i % 3 == 0 else ""
        spans.append(f'<span class="ff{big}"></span>')
    return ('<div class="fireflies" aria-hidden="true">\n      '
            + "\n      ".join(spans) + "\n    </div>")


# -------------------------------------------------------------------- pages --
def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html.rstrip() + "\n")
    print(f"  {path:24s} {len(html) / 1024:6.1f} KB")


HERO_ALT = ALT["forest"]


def build_home():
    title = "The Pinecone Coffee — A little magic in every cup | Puyallup, WA"
    desc = ("A forest-inspired coffee stand in Puyallup, Washington. Espresso, slow "
            "pour-overs, seasonal drinks and forest-inspired bites. Open seven days a week.")
    preload = ('<link rel="preload" as="image" type="image/avif" '
               f'href="/assets/img/forest-1024.avif" imagesrcset="{srcset("forest", "avif")}" '
               'imagesizes="100vw" fetchpriority="high">\n')

    graph = [
        biz_node(), logo_node(), website_node(),
        breadcrumb_node("", "Home"),
        page_node("", "The Pinecone Coffee", desc, "forest"),
    ]

    cards = [
        ("about/", "\N{HERB}", "Our Story", "Where the trees meet your morning.", "Wander in",
         "sack", ALT["sack"]),
        ("menu/", "\N{HOT BEVERAGE}", "The Menu", "Seasonal drinks, espresso &amp; forest-inspired bites.", "Explore",
         "cheers", ALT["cheers"]),
        ("hours/", "\N{EVERGREEN TREE}", "Find Us", "Tucked in the trees in Puyallup, WA.", "Come find us",
         "rainier", ALT["rainier"]),
    ]
    card_html = "\n".join(f"""    <a class="hcard" href="/{href}">
      <span class="media-fill">{picture(img, alt, "(max-width: 640px) 100vw, 33vw")}</span>
      <span class="hcard-content">
        <span class="hcard-icon" aria-hidden="true">{icon}</span>
        <span class="hcard-title">{titl}</span>
        <span class="hcard-desc">{sub}</span>
        <span class="hcard-arrow">{arrow} &rarr;</span>
      </span>
    </a>""" for href, icon, titl, sub, arrow, img, alt in cards)

    return f"""{head(title, desc, "", extra_preload=preload)}
{nav("")}
<main id="main">
  <div class="hero">
    <span class="media-fill">{picture("forest", HERO_ALT, "100vw", lcp=True)}</span>
    <div class="hero-scrim" aria-hidden="true"></div>
    {fireflies()}
    <div class="hero-content">
      <div class="logo-wrap">
        <span class="logo-ring2" aria-hidden="true"></span>
        <span class="logo-ring" aria-hidden="true"></span>
        <picture>
          <source type="image/webp" srcset="/assets/img/logo-210.webp 210w, /assets/img/logo-420.webp 420w" sizes="(max-width: 640px) 40vw, 210px">
          <img class="logo-img" src="/assets/img/logo-420.png"
               srcset="/assets/img/logo-210.png 210w, /assets/img/logo-420.png 420w"
               sizes="(max-width: 640px) 40vw, 210px" width="508" height="496"
               alt="The Pinecone Coffee crest: a crescent moon above a pinecone, framed by ferns"
               fetchpriority="high" decoding="async">
        </picture>
      </div>
      <p class="hero-eyebrow">Est. {BIZ['founded']} &middot; {BIZ['locality']}, {BIZ['region']}</p>
      <h1 class="hero-title">The Pinecone<span class="hero-sub">Coffee</span></h1>
      <p class="hero-tagline">{BIZ['slogan']}</p>
      <a class="btn btn-gold" href="/menu/">See the Menu</a>
    </div>
    <span class="scroll-hint" aria-hidden="true">scroll</span>
  </div>

  <div class="home-cards">
{card_html}
  </div>
</main>
{footer()}
{jsonld(graph)}
</body>
</html>"""


def build_about():
    title = "Our Story — The Pinecone Coffee | Puyallup, WA"
    desc = ("How The Pinecone began: a coffee stand built to feel like a fairy-tale "
            "clearing in the woods, with beans from small Pacific Northwest roasters.")
    graph = [
        biz_node(), logo_node(), website_node(),
        breadcrumb_node("about/", "Our Story"),
        page_node("about/", "Our Story", desc, "forest", page_type="AboutPage"),
    ]
    values = "\n".join(f"""      <div class="vcard">
        <span class="vcard-icon" aria-hidden="true">{icon}</span>
        <h3>{name}</h3>
        <p>{body}</p>
      </div>""" for icon, name, body in VALUES)

    return f"""{head(title, desc, "about/")}
{nav("about/")}
<main id="main">
  <div class="page-hero">
    <span class="media-fill">{picture("forest", HERO_ALT, "100vw", lcp=True)}</span>
    <div class="page-hero-scrim" aria-hidden="true"></div>
    <div class="page-hero-text">
      <p class="eyebrow">Our Story</p>
      <h1 class="heading">Where the forest<br>meets your cup</h1>
    </div>
  </div>

  <div class="about-body">
    <div class="about-grid">
      <div>
        <div class="divider"><span class="divider-icon" aria-hidden="true">&#10022;</span></div>
        <p>The Pinecone started with a dream and a desire for something greater. We wanted to
           create a coffee stand that felt like stumbling into a fairy-tale clearing &mdash;
           somewhere warm, unhurried, and a little bit magical.</p>
        <p>Our beans come from small local roasters and are roasted to bring out every earthy,
           wild note the Pacific Northwest has to offer.
           <em>We believe the best mornings are slow ones, shared over something delicious.</em></p>
        <p>We are your neighbours, your forest friends, and your daily ritual. Come as you are
           &mdash; the mushrooms and ferns do not judge.</p>
        <p><a class="btn btn-ink" href="/menu/">See what we are pouring</a></p>
      </div>
      <div class="about-photo-stack">
        {picture("lattes", ALT["lattes"], "(max-width: 700px) 100vw, 360px", img_cls="aphoto-main")}
        {picture("sack", ALT["sack"], "(max-width: 700px) 55vw, 200px", img_cls="aphoto-accent")}
      </div>
    </div>

    <div class="divider"><span class="divider-icon" aria-hidden="true">&#10022;</span></div>

    <div class="values-grid">
{values}
    </div>
  </div>
</main>
{footer()}
{jsonld(graph)}
</body>
</html>"""


def build_menu():
    title = "Menu — Espresso, Seasonal Drinks & Bites | The Pinecone Coffee"
    desc = ("The full Pinecone Coffee menu: espresso and drip, signature and cold drinks "
            "including The Pinecone, rotating seasonal specials, and bites baked locally.")
    graph = [
        biz_node(on_menu_page=True), logo_node(), website_node(),
        breadcrumb_node("menu/", "Menu"),
        page_node("menu/", "Menu", desc, "cheers",
                  extra={"mainEntity": {"@id": f"{BASE}/menu/#menu"}}),
        menu_node(),
    ]

    jump = "\n".join(f'    <a href="#{s["slug"]}">{s["nav"]}</a>' for s in MENU)

    sections = []
    for section in MENU:
        items = []
        for slug, name, price, sdesc, badge, diets in section["items"]:
            badge_html = f'\n        <p class="ibadge">{badge}</p>' if badge else ""
            diet_html = ""
            if diets:
                labels = " &middot; ".join(DIET_LABEL[d] for d in diets)
                diet_html = f'\n        <span class="idiet">{labels}</span>'
            items.append(f"""      <div class="mitem" id="item-{slug}">{badge_html}
        <div class="mitem-top">
          <span class="iname">{name}</span>
          <span class="iprice">${price}</span>
        </div>
        <p class="idesc">{sdesc}</p>{diet_html}
      </div>""")
        sections.append(f"""  <section class="menu-section" id="{section['slug']}" aria-labelledby="h-{section['slug']}">
    <div class="menu-section-head">
      <h2 id="h-{section['slug']}">{section['name']}</h2>
      <p>{section['blurb']}</p>
    </div>
    <div class="menu-grid">
{chr(10).join(items)}
    </div>
  </section>""")

    addons = "\n".join(
        f'      <li><span>{name}</span> <b>{"no charge" if price == "0.00" else "+$" + price}</b></li>'
        for _, name, price, _ in ADDONS)

    return f"""{head(title, desc, "menu/")}
{nav("menu/")}
<main id="main">
  <div class="page-hero">
    <span class="media-fill">{picture("cheers", ALT["cheers"], "100vw", lcp=True)}</span>
    <div class="page-hero-scrim" aria-hidden="true"></div>
    <div class="page-hero-text">
      <p class="eyebrow">What we are brewing</p>
      <h1 class="heading">The Menu</h1>
    </div>
  </div>

  <div class="menu-body">
    <nav class="menu-jump" aria-label="Menu sections">
{jump}
    </nav>

{chr(10).join(sections)}

    <section class="menu-addons" aria-labelledby="h-addons">
      <h2 id="h-addons">Make it yours</h2>
      <ul class="addon-list">
{addons}
      </ul>
    </section>
  </div>
</main>
{footer()}
{jsonld(graph)}
</body>
</html>"""


def build_hours():
    title = "Hours & Location — The Pinecone Coffee | Puyallup, WA"
    desc = ("When and where to find The Pinecone Coffee in Puyallup, Washington. "
            "Open Monday to Friday 8am–4pm, and weekends 10am–3pm.")
    graph = [
        biz_node(), logo_node(), website_node(),
        breadcrumb_node("hours/", "Hours & Location"),
        page_node("hours/", "Hours & Location", desc, "ridge"),
        faq_node(),
    ]

    rows = "\n".join(
        f"          <tr><th scope=\"row\">{label}</th><td>{human}</td></tr>"
        for _, _, _, label, human in HOURS)

    faqs = "\n".join(f"""      <div class="faq-item">
        <h3>{q}</h3>
        <p>{a}</p>
      </div>""" for q, a in FAQ)

    strip = "\n".join(
        picture(n, a, "(max-width: 560px) 100vw, 300px", img_cls="strip-img")
        for n, a in [("rainier", ALT["rainier"]), ("sack", ALT["sack"]),
                     ("lattes", ALT["lattes"])])

    return f"""{head(title, desc, "hours/")}
{nav("hours/")}
<main id="main">
  <div class="page-hero">
    <span class="media-fill">{picture("ridge", ALT["ridge"], "100vw", lcp=True)}</span>
    <div class="page-hero-scrim" aria-hidden="true"></div>
    <div class="page-hero-text">
      <p class="eyebrow">Come find us</p>
      <h1 class="heading">Hours &amp; Location</h1>
    </div>
  </div>

  <div class="hours-body">
    <div class="divider"><span class="divider-label">We would love to hear from you</span></div>

    <div class="hours-grid">
      <div>
        <table class="htable">
          <caption>When to visit</caption>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
      <div>
        <div class="loc-card">
          <h2>{BIZ['name']}</h2>
          <address>
            {BIZ['locality']}, {BIZ['region']} {BIZ['postal']}<br>
            United States
          </address>
          <p>Look for the pinecone sign &mdash; we are tucked back in the trees, waiting.</p>
          <ul class="contact-list">
            <li>
              <span class="label">Call us</span>
              <a href="tel:{BIZ['phone_e164']}">{BIZ['phone_display']}</a>
            </li>
            <li>
              <span class="label">Email</span>
              <a href="mailto:{BIZ['email']}">{BIZ['email']}</a>
            </li>
            <li>
              <span class="label">Directions</span>
              <a href="{BIZ['map_url']}" rel="noopener">Open in Google Maps</a>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <section class="faq" aria-labelledby="h-faq">
      <h2 id="h-faq">Before you come</h2>
{faqs}
    </section>

    <div class="photo-strip">
{strip}
    </div>
  </div>
</main>
{footer()}
{jsonld(graph)}
</body>
</html>"""


def build_404():
    title = "Page not found — The Pinecone Coffee"
    desc = "That path led somewhere else. Head back to The Pinecone Coffee."
    return f"""{head(title, desc, "404.html")}
{nav(None)}
<main id="main">
  <div class="nf">
    <span class="media-fill">{picture("forest", "", "100vw")}</span>
    <div class="hero-scrim" aria-hidden="true"></div>
    <div class="nf-content">
      <h1>You have wandered off the trail</h1>
      <p>There is nothing at this address &mdash; just ferns, and a bit of mist.
         Let us walk you back.</p>
      <p><a class="btn btn-gold" href="/">Back to the clearing</a></p>
    </div>
  </div>
</main>
{footer()}
</body>
</html>"""


def build_extras():
    pages = [("", "1.0", "weekly"), ("about/", "0.8", "monthly"),
             ("menu/", "0.9", "weekly"), ("hours/", "0.8", "monthly")]
    entries = "\n".join(f"""  <url>
    <loc>{url(p)}</loc>
    <lastmod>{BUILD_DATE}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""" for p, pri, freq in pages)
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>""")

    write("robots.txt", f"""# The Pinecone Coffee

User-agent: *
Allow: /

# Assistants and answer engines are explicitly welcome to read this site.
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {BASE}/sitemap.xml""")

    write("site.webmanifest", json.dumps({
        "name": BIZ["name"],
        "short_name": BIZ["short"],
        "description": BIZ["description"],
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#111f10",
        "theme_color": "#111f10",
        "icons": [
            {"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "maskable"},
        ],
    }, indent=2))

    write(".nojekyll", "")


if __name__ == "__main__":
    print("Building thepineconecoffee.com\n")
    write("index.html", build_home())
    write("about/index.html", build_about())
    write("menu/index.html", build_menu())
    write("hours/index.html", build_hours())
    write("404.html", build_404())
    build_extras()
    n = sum(len(s["items"]) for s in MENU) + len(ADDONS)
    print(f"\nDone. {n} menu items marked up, {len(FAQ)} FAQ entries.")
