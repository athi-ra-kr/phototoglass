from io import BytesIO
from decimal import Decimal
from PIL import Image, ImageDraw
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from store.models import (SiteConfig, Banner, Product, Faq, ProductCategory,
                          CollectionCategory, Collection, CollectionImage, CollectionDimension,
                          BlogPost, BeforeAfter, CustomerStory,
                          BackgroundShape, BackgroundShapeDimension, BackgroundImage, BackgroundColor,
                          BackgroundFrame, BackgroundStand, PortraitShape, PortraitShapeDimension, PortraitImage, PortraitFrame, Embellishment)


def grad_image(c1, c2, w=900, h=650):
    strip = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / h
        strip.putpixel((0, y), tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    img = strip.resize((w, h))
    buf = BytesIO(); img.save(buf, "JPEG", quality=82)
    return ContentFile(buf.getvalue())


def frame_png(color=(201, 138, 43), w=900, h=650, border=26, oval=False):
    """A transparent-centre frame so it never hides the design underneath."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if oval:
        for i in range(border):
            d.ellipse([i, i, w - 1 - i, h - 1 - i], outline=color + (255,))
    else:
        for i in range(border):
            d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=color + (255,))
    buf = BytesIO(); img.save(buf, "PNG")
    return ContentFile(buf.getvalue())


BANNERS = [
    ("Light, captured in glass", "Shop ready-made coastal collections, personalize a gift in minutes, or design every layer yourself — then we print it on premium 5 mm glass and deliver free.", (4, 50, 59), (127, 214, 201)),
    ("Personalised gifts they'll keep", "Add a name, a date and your own photo. Heartfelt keepsakes printed on premium glass, proofed free before we print.", (74, 19, 48), (255, 209, 232)),
    ("Design it yourself", "Layer text, shapes and images in our studio — drag, zoom and rotate until it's exactly right.", (4, 34, 43), (191, 247, 236)),
    ("Made-to-measure splashbacks", "Heat- and scratch-resistant printed glass splashbacks, cut to fit your kitchen.", (6, 59, 63), (174, 240, 201)),
]
PCATS = ["Wall Art", "Kitchen Splashbacks", "Gallery Wall Sets", "Birthday Gifts", "Wedding Gifts", "Design Your Own"]
PRODUCTS = [
    ("Coastal Dawn", "Wall Art", "fixed", 89, "🌊", "linear-gradient(135deg,#0a4f5c,#1d8a9e 60%,#7fd6c9)"),
    ("Azure Splashback", "Kitchen Splashbacks", "fixed", 145, "🍃", "linear-gradient(135deg,#063b3f,#108a7a 70%,#aef0c9)"),
    ("Gallery Tide Set", "Gallery Wall Sets", "fixed", 210, "🐚", "linear-gradient(135deg,#13324d,#3a6ea5 70%,#bcd9ff)"),
    ("Birthday Bloom", "Birthday Gifts", "personalise", 54, "🎂", "linear-gradient(135deg,#5c1f49,#b85c8a 70%,#ffd1e8)"),
    ("Eternal Vows", "Wedding Gifts", "personalise", 78, "💍", "linear-gradient(135deg,#3d2c52,#8f6fb0 70%,#efe2ff)"),
    ("Blank Canvas", "Design Your Own", "personalise", 0, "✨", "linear-gradient(135deg,#04222b,#0fb6a2 75%,#bff7ec)"),
    ("Studio Freeform", "Design Your Own", "personalise", 0, "🎨", "linear-gradient(135deg,#102a3a,#2fb7c9 70%,#cdfcff)"),
]
CATS = [
    ("Abstract Art", (74, 29, 110), (192, 108, 240)),
    ("Landscape / Nature", (10, 79, 92), (127, 214, 201)),
    ("Wildlife / Botanical", (6, 59, 63), (174, 240, 201)),
    ("Religious & Spiritual", (61, 44, 82), (239, 226, 255)),
    ("Modern / Digital Art", (16, 42, 58), (47, 183, 201)),
    ("Golden Hour & Silhouettes", (122, 47, 58), (240, 201, 135)),
]
FAQS = [
    ("What glass do you print on?", "Premium 5 mm toughened glass with a scratch- and UV-resistant printed surface. Additional thicknesses are coming soon."),
    ("How long does an order take?", "Most orders are proofed within 1 business day and delivered 3–5 working days after you approve the proof."),
    ("Can I use my own photo?", "Yes — upload it in the design studio or in a personalize-ready product. See our Photo Preparation Guide for best results."),
    ("Do you ship outside Mauritius?", "Local delivery is free. For international or trade shipping, use the B2B quote request form."),
]


class Command(BaseCommand):
    help = "Seed demo content"

    def handle(self, *args, **opts):
        SiteConfig.get()

        if not Banner.objects.exists():
            for i, (t, d, c1, c2) in enumerate(BANNERS):
                b = Banner(title=t, description=d, order=i,
                           btn1_text="Design yours now", btn1_link="/studio/",
                           btn2_text="Browse collections", btn2_link="/collections/")
                b.image.save(f"banner{i}.jpg", grad_image(c1, c2), save=True)

        pcat_map = {}
        if not ProductCategory.objects.exists():
            for i, name in enumerate(PCATS):
                pcat_map[name] = ProductCategory.objects.create(name=name, description="Printed on premium 5 mm glass", order=i)
        else:
            pcat_map = {c.name: c for c in ProductCategory.objects.all()}

        if not Product.objects.exists():
            pc = [(10,79,92),(6,59,63),(19,50,77),(92,31,73),(61,44,82),(4,34,43),(16,42,58)]
            for i, (n, cat, t, p, m, g) in enumerate(PRODUCTS):
                prod = Product(name=n, category=pcat_map.get(cat), product_type=t, price=p,
                               order=i, stock=10)
                c1 = pc[i % len(pc)]; c2 = tuple(min(255, x + 120) for x in c1)
                prod.image.save(f"prod{i}.jpg", grad_image(c1, c2), save=True)

        if not Faq.objects.exists():
            for i, (q, a) in enumerate(FAQS):
                Faq.objects.create(question=q, answer=a, order=i)

        if not CollectionCategory.objects.exists():
            for i, (name, c1, c2) in enumerate(CATS):
                cat = CollectionCategory.objects.create(name=name, description="Printed on premium 5 mm glass", order=i)
                for j in range(2):
                    col = Collection.objects.create(category=cat, title=f"{name.split(' /')[0]} #{j+1}",
                                                    description="A demo piece — replace with your own image and details.")
                    ci = CollectionImage(collection=col); ci.image.save(f"cat{i}_{j}.jpg", grad_image(c1, c2), save=True)
                    CollectionDimension.objects.create(collection=col, width_cm=25, height_cm=35, price=Decimal("69"), stock=10)
                    CollectionDimension.objects.create(collection=col, width_cm=40, height_cm=60, price=Decimal("119"), stock=6)

        if not BlogPost.objects.exists():
            posts = [
                ("5 ways to style glass wall art", "Make your prints sing with these quick styling tips.", (10, 79, 92), (127, 214, 201)),
                ("Choosing the perfect gift", "From birthdays to weddings — a gifting guide.", (92, 31, 73), (255, 209, 232)),
                ("Behind the glass: our process", "How a photo becomes a finished glass print.", (16, 42, 58), (47, 183, 201)),
                ("Caring for your glass print", "Keep it brilliant for years with these tips.", (6, 59, 63), (174, 240, 201)),
            ]
            for (t, e, c1, c2) in posts:
                b = BlogPost(title=t, excerpt=e,
                             body="This is **demo** content. You can write *italics*, paragraphs and lists:\n\n- Point one\n- Point two\n- Point three\n\nReplace this in the dashboard.")
                b.image.save(f"blog_{t[:6]}.jpg", grad_image(c1, c2), save=True)

        if not BeforeAfter.objects.exists():
            for i in range(2):
                ba = BeforeAfter(title=f"Project #{i+1}", caption="From phone photo to glass art.", order=i)
                ba.before_image.save(f"before{i}.jpg", grad_image((60, 60, 60), (120, 120, 120)), save=True)
                ba.after_image.save(f"after{i}.jpg", grad_image((10, 79, 92), (127, 214, 201)), save=True)

        if not CustomerStory.objects.exists():
            stories = [("Aanya", "Curepipe", "The arch piece is the first thing guests notice."),
                       ("Devan & Priya", "Flic en Flac", "Turned our wedding photo into an heirloom."),
                       ("Le Morne Villa", "Le Morne", "The splashback totally changed our kitchen."),
                       ("Sara", "Grand Baie", "Beautiful quality and so easy to design online.")]
            for i, (n, loc, txt) in enumerate(stories):
                s = CustomerStory(name=n, location=loc, story=txt, rating=5, order=i)
                s.image.save(f"story{i}.jpg", grad_image((61, 44, 82), (239, 226, 255)), save=True)

        # ---- Design Studio Assets ----
        DIMS_PORTRAIT  = [(25, 35, "49"), (35, 50, "69"), (40, 60, "89"), (60, 85, "129")]
        DIMS_LANDSCAPE = [(35, 25, "49"), (50, 35, "69"), (60, 40, "89"), (85, 60, "129")]
        if not BackgroundShape.objects.exists():
            shapedims = {"Rectangle Landscape": DIMS_LANDSCAPE, "Rectangle Portrait": DIMS_PORTRAIT}
            for i, sname in enumerate(["Rectangle Landscape", "Rectangle Portrait"]):
                sh = BackgroundShape.objects.create(name=sname, order=i)
                for (w, h, p) in shapedims[sname]:
                    BackgroundShapeDimension.objects.create(shape=sh, width_cm=w, height_cm=h, base_price=Decimal(p))
        shapes = list(BackgroundShape.objects.all())

        if not BackgroundImage.objects.exists():
            themes = [("Ocean Wave", (10, 79, 92), (127, 214, 201)),
                      ("Sunset", (122, 47, 58), (240, 201, 135)),
                      ("Lagoon", (12, 90, 96), (170, 235, 220)),
                      ("Forest", (6, 59, 63), (174, 240, 201))]
            n = 0
            for sh in shapes:
                for dim in sh.dimensions.all():
                    # two background images per exact size (aspect matches the size)
                    for t in range(2):
                        nm, c1, c2 = themes[(n + t) % len(themes)]
                        bi = BackgroundImage(name=f"{nm} · {dim.label}", dimension=dim, order=n)
                        bi.image.save(f"bg{n}.jpg", grad_image(c1, c2, dim.width_cm * 22, dim.height_cm * 22), save=True); n += 1

        if not BackgroundFrame.objects.exists():
            styles = ["Thin Gold", "Simple White", "Classic Black", "Rustic Wood"]
            j = 0
            for sh in shapes:
                for dim in sh.dimensions.all():
                    bf = BackgroundFrame(dimension=dim, name=styles[j % len(styles)], order=j)
                    bf.image.save(f"bgframe{j}.png", frame_png((201, 138, 43), dim.width_cm * 22, dim.height_cm * 22), save=True); j += 1

        if not BackgroundStand.objects.exists():
            standdefs = [("Wooden Easel Stand", (120, 84, 44), (196, 158, 104), "Rectangle Landscape"),
                         ("Gold Table Stand", (150, 116, 40), (222, 190, 120), "Rectangle Portrait")]
            for k, (nm, c1, c2, shname) in enumerate(standdefs):
                st = BackgroundStand(name=nm, order=k)
                st.image.save(f"standdemo{k}.jpg", grad_image(c1, c2, 320, 320), save=True)
                sh = BackgroundShape.objects.filter(name=shname).first()
                if sh:
                    st.shapes.set([sh])

        if not BackgroundColor.objects.exists():
            for i, (nm, col) in enumerate([("Ocean Teal", "linear-gradient(135deg,#0a4f5c,#7fd6c9)"),
                                           ("Blush", "linear-gradient(135deg,#5c1f49,#ffd1e8)"),
                                           ("Slate", "#0b2a30")]):
                BackgroundColor.objects.create(name=nm, color=col, order=i)

        if not PortraitShape.objects.exists():
            # fixed shapes (outline is coded in the studio, not uploaded). One small size each
            # (the photo can be zoomed/rotated in the studio, so a single size is enough).
            shapedefs = [("Square", "square", (8, 8)), ("Heart", "heart", (9, 9)),
                         ("Circle", "circle", (8, 8)), ("Oval", "oval", (8, 12))]
            for i, (nm, key, (w, h)) in enumerate(shapedefs):
                ps = PortraitShape.objects.create(name=nm, key=key, order=i)
                PortraitShapeDimension.objects.create(shape=ps, width_cm=w, height_cm=h, order=0)
        pshapes = list(PortraitShape.objects.all())

        if not PortraitImage.objects.exists():
            pdefs = [("Family", (60, 40, 80), (200, 180, 230)),
                     ("Pet", (90, 60, 30), (220, 190, 150))]
            n = 0
            for ps in pshapes:
                dim = ps.dimensions.first()
                for (nm, c1, c2) in pdefs:
                    pi = PortraitImage(name=nm, dimension=dim, order=n)
                    pi.image.save(f"pimg{n}.jpg", grad_image(c1, c2, int(float(dim.width_cm) * 40), int(float(dim.height_cm) * 40)), save=True); n += 1

        if not PortraitFrame.objects.exists():
            j = 0
            for ps in pshapes:
                dim = ps.dimensions.first()
                pf = PortraitFrame(dimension=dim, name="Gold Outline", order=j)
                pf.image.save(f"pframe{j}.png", frame_png((201, 138, 43), int(float(dim.width_cm) * 40), int(float(dim.height_cm) * 40), border=18, oval=(ps.key in ("circle", "oval"))), save=True); j += 1

        if not Embellishment.objects.exists():
            for i, (nm, c1, c2, wd, ht) in enumerate([("Star", (240, 201, 135), (255, 240, 200), 60, 60),
                                                      ("Leaf", (6, 80, 60), (170, 240, 200), 80, 80),
                                                      ("Heart sticker", (180, 60, 110), (255, 200, 220), 70, 70)]):
                em = Embellishment(name=nm, width=wd, height=ht, order=i)
                em.image.save(f"stk{i}.png", grad_image(c1, c2, 200, 200), save=True)

        self.stdout.write(self.style.SUCCESS("Seeded content (with placeholder images)."))
