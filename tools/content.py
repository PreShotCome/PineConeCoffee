"""
Single source of truth for The Pinecone Coffee.

Both the visible HTML and the JSON-LD structured data are generated from the
data in this file, so the markup can never drift out of sync with the page —
which is a hard requirement: search engines discount structured data that
describes things a visitor cannot see.

The Pinecone Coffee is a CONCEPT BRAND — a design showcase, not a trading
business. That is why there is no street address, no geo pin and no sameAs
profiles here: publishing an invented location or a dead social link would be
worse than publishing nothing. The phone number is inside the 555-01xx range,
which is permanently reserved for fictional use.
"""

BASE = "https://www.thepineconecoffee.com"
BUILD_DATE = "2026-08-11"

BIZ = {
    "name": "The Pinecone Coffee",
    "short": "The Pinecone",
    "slogan": "A little magic in every cup",
    "founded": "2026",
    "locality": "Puyallup",
    "region": "WA",
    "postal": "98371",
    "country": "US",
    "phone_display": "(253) 555-0147",
    "phone_e164": "+1-253-555-0147",
    "email": "hello@thepineconecoffee.com",
    "price_range": "$$",
    "map_url": "https://www.google.com/maps/search/?api=1&query=Puyallup%2C+WA+98371",
    "description": (
        "A forest-inspired coffee stand in Puyallup, Washington. Espresso, "
        "slow pour-overs, seasonal drinks and forest-inspired bites, served "
        "somewhere warm, unhurried and a little bit magical."
    ),
    "concept_note": (
        "The Pinecone Coffee is a concept brand created as a design and build "
        "showcase. It is not a trading business, and the location and telephone "
        "number shown are illustrative."
    ),
}

# day -> (opens, closes) in 24h. Used for both the table and openingHoursSpecification.
HOURS = [
    (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "08:00", "16:00",
     "Monday – Friday", "8:00 am – 4:00 pm"),
    (["Saturday"], "10:00", "15:00", "Saturday", "10:00 am – 3:00 pm"),
    (["Sunday"], "10:00", "15:00", "Sunday", "10:00 am – 3:00 pm"),
]

AMENITIES = [
    ("Walk-up window", True),
    ("Outdoor seating", True),
    ("Dog friendly", True),
    ("Wheelchair accessible", True),
    ("Free Wi-Fi", True),
    ("Indoor seating", False),
]

VEGAN = "https://schema.org/VeganDiet"
GF = "https://schema.org/GlutenFreeDiet"
VEGETARIAN = "https://schema.org/VegetarianDiet"

DIET_LABEL = {VEGAN: "Vegan", GF: "Gluten free", VEGETARIAN: "Vegetarian"}

# (slug, name, price, description, badge, diets)
MENU = [
    {
        "slug": "espresso",
        "name": "Espresso & Drip",
        "nav": "Espresso/Drip",
        "blurb": "The everyday backbone. Beans from small Pacific Northwest roasters, "
                 "pulled and poured the same way every morning.",
        "items": [
            ("espresso", "Espresso", "2.75", "Two ounces, pulled short and syrupy. Nothing to hide behind.", None, []),
            ("macchiato", "Macchiato", "3.50", "Espresso marked with a spoonful of foam. Small and serious.", None, [VEGETARIAN]),
            ("drip", "Drip Coffee", "3.25", "A rotating single origin, brewed by the batch. Ask what is in the hopper.", None, [VEGAN]),
            ("americano", "Americano", "3.75", "Espresso lengthened with hot water, crema intact.", None, [VEGAN]),
            ("cortado", "Cortado", "4.25", "Equal parts espresso and steamed milk, served in a warm glass.", None, [VEGETARIAN]),
            ("cappuccino", "Cappuccino", "4.50", "Dense foam, a dusting of cocoa, the way it is meant to be.", None, [VEGETARIAN]),
            ("flat-white", "Flat White", "4.75", "Silky microfoam, a double ristretto underneath.", None, [VEGETARIAN]),
            ("latte", "Latte", "4.75", "Twelve, sixteen or twenty ounces of quiet.", None, [VEGETARIAN]),
            ("pour-over", "Pour-Over", "5.25", "Four minutes, one cup, no rushing. The slowest thing we make.", "Made to order", [VEGAN]),
        ],
    },
    {
        "slug": "signature",
        "name": "Signature & Cold",
        "nav": "Signature/Cold",
        "blurb": "The drinks you cannot get anywhere else, and the cold ones that "
                 "get us through a Washington August.",
        "items": [
            ("the-pinecone", "The Pinecone", "6.25",
             "Our namesake. Spruce-tip syrup, dark chocolate and cream over a double shot — "
             "resinous, sweet and faintly wild. The one people come back for.", "House signature", [VEGETARIAN]),
            ("forest-floor-mocha", "Forest Floor Mocha", "6.00",
             "Dark chocolate, a whisper of smoked sea salt and a dusting of cocoa nib.", None, [VEGETARIAN]),
            ("fern-and-honey", "Fern & Honey", "5.75",
             "Honey, lavender and cracked vanilla steamed into whole milk.", None, [VEGETARIAN]),
            ("chaga-mocha", "Chaga Mocha", "6.50",
             "Chaga mushroom, raw cacao and maple. Earthy, grounding, faintly medicinal in a good way.", None, [VEGAN]),
            ("cold-brew", "Cold Brew", "4.75",
             "Steeped eighteen hours. Bold, low-acid and unwise on an empty stomach.", None, [VEGAN]),
            ("nitro", "Nitro Cold Brew", "5.50",
             "Cascading, cream-topped, and there is no cream in it.", None, [VEGAN]),
            ("mossbeam", "Mossbeam Matcha", "5.75",
             "Stone-ground ceremonial matcha, oat milk, a thread of wildflower honey.", None, [VEGETARIAN]),
            ("lavender-fog", "Iced Lavender Fog", "5.50",
             "Earl Grey, lavender and cold milk over a tall glass of ice.", None, [VEGETARIAN]),
        ],
    },
    {
        "slug": "seasonal",
        "name": "Seasonal",
        "nav": "Seasonal",
        "blurb": "Our specials follow the forest's rhythm — wild, slow, and always changing. "
                 "These rotate; if one is gone, it will come back around.",
        "items": [
            ("spruce-tip-latte", "Spruce Tip Latte", "6.00",
             "Bright green spring tips, steeped into syrup. Tastes like the first warm week.", "Spring", [VEGETARIAN]),
            ("blackberry-cold-foam", "Wild Blackberry Cold Foam", "6.25",
             "Roadside blackberries folded into salted cold foam over cold brew.", "Summer", [VEGETARIAN]),
            ("smoked-maple-cortado", "Smoked Maple Cortado", "5.75",
             "Alder-smoked maple, a double shot, and just enough milk to soften it.", "Autumn", [VEGETARIAN]),
            ("douglas-fir-cocoa", "Douglas Fir Hot Chocolate", "5.50",
             "Real drinking chocolate infused with fir needle. Christmas tree, but delicious.", "Winter", [VEGETARIAN]),
            ("rainier-soda", "Rainier Cherry Italian Soda", "4.75",
             "Cherry, soda water, a splash of cream if you want the cloud.", "Summer", [VEGAN]),
            ("nettle-mint", "Nettle & Mint Tea", "3.75",
             "Foraged nettle and garden mint. Caffeine-free and quietly restorative.", None, [VEGAN, GF]),
        ],
    },
    {
        "slug": "bites",
        "name": "Bites",
        "nav": "Bites",
        "blurb": "Baked a few miles from here and delivered before we open. "
                 "When they are gone, they are gone.",
        "items": [
            ("morning-bun", "Morning Bun", "4.25", "Laminated, orange-scented, rolled in cinnamon sugar.", None, [VEGETARIAN]),
            ("fir-honey-scone", "Hazelnut & Fir Honey Scone", "4.50", "Toasted hazelnut, crackly top, fir honey glaze.", None, [VEGETARIAN]),
            ("cardamom-knot", "Cardamom Knot", "4.75", "Twisted, pearl-sugared, best eaten warm and immediately.", None, [VEGETARIAN]),
            ("sourdough-toast", "Sourdough Toast", "4.00", "Thick-cut country loaf, cultured butter, seasonal jam.", None, [VEGETARIAN]),
            ("mushroom-hand-pie", "Mushroom & Gruyère Hand Pie", "7.25", "Wild mushrooms, nutty gruyère, all-butter pastry.", None, [VEGETARIAN]),
            ("blackberry-oat-bar", "Oat & Blackberry Bar", "4.00", "Chewy, jammy, and it happens to be vegan and gluten free.", None, [VEGAN, GF]),
        ],
    },
]

# Add-ons are marked up as MenuItems and referenced from drinks via menuAddOn.
ADDONS = [
    ("oat-milk", "Oat, almond or soy milk", "0.75", "Swap the dairy for any of the three."),
    ("extra-shot", "Extra espresso shot", "1.25", "For the mornings that need it."),
    ("syrup", "House syrup", "0.75", "Vanilla, spruce tip, lavender or smoked maple."),
    ("cold-foam", "Salted cold foam", "1.00", "Poured over the top of anything cold."),
    ("decaf", "Decaf", "0.00", "Swiss-water process, no charge."),
]

FAQ = [
    ("Where is The Pinecone Coffee?",
     "We are in Puyallup, Washington, tucked back in the trees. Look for the pinecone sign."),
    ("What are your opening hours?",
     "Monday to Friday from 8:00 am to 4:00 pm, and Saturday and Sunday from 10:00 am to 3:00 pm."),
    ("Do you have non-dairy milk?",
     "Yes — oat, almond and soy, for seventy-five cents. Several drinks are made with oat milk by default."),
    ("Is there anything gluten free or vegan?",
     "Yes. The oat and blackberry bar is both, the nettle and mint tea is both, and every espresso drink can be made vegan with a milk swap."),
    ("Can I bring my dog?",
     "Please do. We are a walk-up window with outdoor seating, and there is usually a biscuit behind the counter."),
    ("Do you take cards?",
     "Cards, Apple Pay and Google Pay, plus cash if you still carry it."),
]

VALUES = [
    ("\N{HERB}", "Sustainably Sourced",
     "Every bean chosen with care, from small roasters who love the land as much as we do."),
    ("\N{EVERGREEN TREE}", "Forest Rooted",
     "Proudly Puyallup. Rainier is always in our hearts, and we are part of this place."),
    ("\N{MAPLE LEAF}", "Seasonally Inspired",
     "Our specials follow the forest's rhythm — wild, slow, and always changing."),
]


def all_menu_items():
    for section in MENU:
        for item in section["items"]:
            yield section, item
