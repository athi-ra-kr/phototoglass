from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
from .pdfgen import build_order_pdf
from .models import (Product, Banner, Faq, ProductCategory, CollectionCategory, Collection,
                     CollectionDimension, BlogPost, BeforeAfter, CustomerStory,
                     Order, OrderItem,
                     BackgroundShape, BackgroundImage, BackgroundColor, BackgroundFrame, BackgroundStand,
                     PortraitShape, PortraitImage, PortraitFrame, Embellishment, ProductConfig)
from .forms import QuoteForm, ContactForm

SHAPES = [
    ("rect-landscape", "Rectangle Landscape"), ("rect-portrait", "Rectangle Portrait"),
    ("full-arc", "Full Arc"), ("side-arc", "Side Arc"),
    ("heart", "Heart"), ("orient", "Orient"), ("wave", "Wave"),
]
SIZES = ["25 × 35 cm", "35 × 50 cm", "40 × 60 cm", "60 × 85 cm"]


HIW_STEPS = [
    (1, "Choose or design", "Pick a ready-made piece, personalize a gift, or build your own in the design studio."),
    (2, "We proof it", "You receive a free digital proof to approve before anything is printed."),
    (3, "We print & deliver", "Printed on premium 5 mm glass and delivered free across Mauritius."),
]

def home(request):
    return render(request, "store/home.html", {
        "banners": Banner.objects.filter(active=True),
        "product_categories": ProductCategory.objects.filter(active=True)[:6],
        "collection_categories": CollectionCategory.objects.filter(active=True)[:6],
        "posts": BlogPost.objects.filter(active=True)[:4],
        "stories": CustomerStory.objects.filter(active=True)[:4],
        "steps": HIW_STEPS,
        "faqs": Faq.objects.all()[:6],
    })

def products(request):
    return render(request, "store/products.html",
                  {"products": Product.objects.filter(active=True), "pcats": ProductCategory.objects.filter(active=True)})

def products_category(request, pk):
    cat = get_object_or_404(ProductCategory, pk=pk, active=True)
    return render(request, "store/products.html",
                  {"products": cat.products.filter(active=True), "pcats": ProductCategory.objects.filter(active=True), "pcat": cat})

def product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk, active=True)
    if request.method == "POST":
        if p.is_personalise:
            messages.info(request, "This product must be personalised in the studio before it can be added to your cart.")
            return redirect("product_detail", pk=p.id)
        _add(request, key=f"product:{p.id}:", name=p.name, detail="", price=p.price,
             qty=int(request.POST.get("qty", 1)), grad=p.gradient, motif=p.motif,
             img=p.image.url if p.image else "")
        messages.success(request, f"Added “{p.name}” to your cart.")
        return redirect("cart")
    # For each active config, find the Background Stand (if any) that matches the shape
    # it was built on — shown read-only next to the config; nothing for the customer to pick.
    stands = list(BackgroundStand.objects.filter(active=True).prefetch_related("shapes"))
    active_configs = list(p.configs.filter(active=True))
    for cfg in active_configs:
        shape_id = (cfg.design or {}).get("shape")
        cfg.stand = next((s for s in stands if shape_id and s.shapes.filter(id=shape_id).exists()), None)
    return render(request, "store/product_detail.html", {"p": p, "sizes": SIZES, "active_configs": active_configs})


# ---------- Collections ----------
def collections(request):
    cats = CollectionCategory.objects.filter(active=True)
    return render(request, "store/collections.html", {"categories": cats})

def category(request, pk):
    cat = get_object_or_404(CollectionCategory, pk=pk, active=True)
    items = cat.collections.filter(active=True)
    return render(request, "store/category.html", {"cat": cat, "items": items})

def collection_detail(request, pk):
    col = get_object_or_404(Collection, pk=pk, active=True)
    dims = col.dimensions.all()
    if request.method == "POST":
        dim = get_object_or_404(CollectionDimension, pk=request.POST.get("dimension"), collection=col)
        _add(request, key=f"collection:{col.id}:{dim.id}", name=col.title, detail=dim.label,
             price=dim.price, qty=int(request.POST.get("qty", 1)), grad="", motif="",
             img=col.thumb_url)
        messages.success(request, f"Added “{col.title}” ({dim.label}) to your cart.")
        return redirect("cart")
    return render(request, "store/collection_detail.html", {"col": col, "dims": dims})


# ---------- B2B (static content + working quote form) ----------
def b2b(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False); lead.kind = "quote"; lead.save()
            messages.success(request, "Quote request sent — we’ll reply within one business day.")
            return redirect("b2b")
    else:
        form = QuoteForm()
    segments = [
        ("Corporate Awards", "Recognition pieces that last", "Custom etched-look trophies and awards printed on premium glass — perfect for staff milestones and partner gifts.", "🏆"),
        ("Hotels & Hospitality", "Signature art at scale", "Coordinated wall art, room numbers and wayfinding produced to a consistent brand standard across your property.", "🏨"),
        ("Photographers", "Sell your work on glass", "Turn your portfolio into premium glass prints with trade pricing and white-label delivery to your clients.", "📷"),
        ("Interior Designers", "Bespoke sizes for projects", "Made-to-measure pieces, trade pricing and project support for residential and commercial fit-outs.", "🛋️"),
    ]
    return render(request, "store/b2b.html", {"form": form, "segments": segments})


# ---------- Inspiration ----------
def inspiration(request):
    return render(request, "store/inspiration.html", {
        "posts": BlogPost.objects.filter(active=True)[:3],
    })

def blog(request):
    return render(request, "store/blog_list.html", {"posts": BlogPost.objects.filter(active=True)})

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, active=True)
    more = BlogPost.objects.filter(active=True).exclude(pk=pk)[:3]
    return render(request, "store/blog_detail.html", {"post": post, "more": more})

def before_after(request):
    return render(request, "store/before_after.html", {"items": BeforeAfter.objects.filter(active=True)})

def size_guide(request):
    rows = [("25 × 35 cm", "Desk / shelf", "Small spaces, gifts"),
            ("35 × 50 cm", "Above a console", "Hallways, bedrooms"),
            ("40 × 60 cm", "Statement piece", "Living rooms"),
            ("60 × 85 cm", "Feature wall", "Large open spaces")]
    return render(request, "store/size_guide.html", {"rows": rows})

def photo_guide(request):
    tips = [("Use the highest resolution", "Aim for at least 2000 px on the long edge so prints stay crisp."),
            ("Good, even lighting", "Natural daylight beats harsh flash; avoid heavy shadows."),
            ("Mind the crop", "Leave a little space around the subject so nothing important is trimmed."),
            ("Avoid heavy filters", "We colour-correct for glass; over-filtered photos can look flat.")]
    return render(request, "store/photo_guide.html", {"tips": tips})

def customer_stories(request):
    return render(request, "store/customer_stories.html", {"stories": CustomerStory.objects.filter(active=True)})


# ---------- Static single pages ----------
def howitworks(request):
    return render(request, "store/howitworks.html", {"steps": HIW_STEPS, "faqs": Faq.objects.all()})

def about(request):
    return render(request, "store/about.html", {})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False); lead.kind = "contact"; lead.save()
            messages.success(request, "Message sent — we’ll be in touch shortly.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "store/contact.html", {"form": form})

def studio(request):
    mode = request.GET.get("mode", "free")  # free | config | locked
    design = None
    product_id = request.GET.get("product") or ""
    config_id = request.GET.get("config") or ""
    config = None
    if config_id:
        config = get_object_or_404(ProductConfig, pk=config_id)
        design = config.design
        product_id = str(config.product_id)
        if mode == "free":
            mode = "locked"
    ctx = {
        "mode": mode,
        "product_id": product_id,
        "config_id": config_id,
        "design_json": json.dumps(design) if design else "null",
        "config_name": config.name if config else "",
        "config_price_json": json.dumps(float(config.price_override) if (config and config.price_override) else None),
    }
    return render(request, "store/studio.html", ctx)


def studio_save_config(request):
    if request.method != "POST" or not request.user.is_staff:
        return redirect("studio")
    pid = request.POST.get("product")
    product = get_object_or_404(Product, pk=pid)
    name = request.POST.get("name", "Configuration")[:120]
    try:
        design = json.loads(request.POST.get("design", "null"))
    except Exception:
        design = None
    config_id = request.POST.get("config_id")
    if config_id:
        cfg = get_object_or_404(ProductConfig, pk=config_id)
        cfg.name = name
        cfg.design = design
        cfg.save()
        messages.success(request, "Configuration updated.")
    else:
        cfg = ProductConfig.objects.create(product=product, name=name, design=design)
        messages.success(request, "Configuration saved.")
    return redirect("dash_product_configs", pk=product.id)


def account(request):
    return render(request, "store/account.html", {})


# ---------- Studio assets API + add ----------
def studio_assets(request):
    data = {
        "shapes": [{"id": s.id, "name": s.name,
                    "dimensions": [{"id": d.id, "label": d.label, "w": d.width_cm, "h": d.height_cm, "price": float(d.base_price)} for d in s.dimensions.all()]}
                   for s in BackgroundShape.objects.filter(active=True)],
        "bg_images": [{"id": b.id, "name": b.name, "url": b.image.url, "shape": b.shape_id, "dimension": b.dimension_id} for b in BackgroundImage.objects.filter(active=True)],
        "bg_colors": [{"id": c.id, "name": c.name, "color": c.color} for c in BackgroundColor.objects.filter(active=True)],
        "bg_frames": [{"id": f.id, "name": f.name, "url": f.image.url, "shape": f.shape_id, "dimension": f.dimension_id} for f in BackgroundFrame.objects.filter(active=True)],
        "background_stands": [{"id": s.id, "name": s.name, "url": s.image.url,
                               "shapes": list(s.shapes.values_list("id", flat=True))} for s in BackgroundStand.objects.filter(active=True)],
        "portrait_shapes": [{"id": p.id, "name": p.name, "key": p.key,
                             "dims": [{"id": d.id, "label": d.label, "w": float(d.width_cm), "h": float(d.height_cm)} for d in p.dimensions.all()]}
                            for p in PortraitShape.objects.filter(active=True).prefetch_related("dimensions")],
        "portrait_images": [{"id": p.id, "name": p.name, "url": p.image.url, "portrait_shape": p.portrait_shape_id, "dimension": p.dimension_id} for p in PortraitImage.objects.filter(active=True)],
        "portrait_frames": [{"id": f.id, "name": f.name, "url": f.image.url, "portrait_shape": f.portrait_shape_id, "dimension": f.dimension_id} for f in PortraitFrame.objects.filter(active=True)],
        "stickers": [{"id": s.id, "name": s.name, "url": s.image.url, "w": s.width, "h": s.height} for s in Embellishment.objects.filter(active=True)],
    }
    return JsonResponse(data)


def studio_add(request):
    if request.method != "POST":
        return redirect("studio")
    import uuid
    name = request.POST.get("name", "Custom design")[:120]
    detail = request.POST.get("detail", "")[:120]
    try:
        price = Decimal(request.POST.get("price", "0"))
    except Exception:
        price = Decimal("0")
    design = request.POST.get("design", "")
    render = request.POST.get("image", "")
    _add(request, key=f"studio:{uuid.uuid4().hex[:8]}", name=name, detail=detail, price=price, qty=1,
         grad="linear-gradient(135deg,#04222b,#0fb6a2 75%,#bff7ec)", motif="🎨", img="", design=design, render=render)
    messages.success(request, "Your design was added to the cart.")
    return redirect("cart")


# ---------- Cart (session) ----------
def _add(request, key, name, detail, price, qty, grad="", motif="", img="", design="", render=""):
    cart = request.session.get("cart", {})
    if key in cart:
        cart[key]["qty"] += qty
    else:
        cart[key] = {"name": name, "detail": detail, "price": str(price), "qty": qty,
                     "grad": grad, "motif": motif, "img": img, "design": design, "render": render}
    request.session["cart"] = cart

def cart_remove(request, key):
    cart = request.session.get("cart", {})
    cart.pop(key, None)
    request.session["cart"] = cart
    return redirect("cart")

def cart(request):
    cart = request.session.get("cart", {})
    items, total = [], Decimal("0")
    for key, it in cart.items():
        price = Decimal(it["price"])
        line = price * it["qty"]
        total += line
        items.append({"key": key, **it, "price": price, "line": line})
    return render(request, "store/cart.html", {"items": items, "total": total})

def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")
    total = sum(Decimal(it["price"]) * it["qty"] for it in cart.values())
    order = Order.objects.create(total=total, customer_name=request.POST.get("name", ""))
    for it in cart.values():
        dz = it.get("design") or None
        if dz:
            try:
                dz = json.loads(dz)
            except Exception:
                dz = None
        oi = OrderItem(order=order, title=it["name"], detail=it.get("detail", ""),
                       qty=it["qty"], unit_price=Decimal(it["price"]), design=dz)
        rnd = it.get("render") or ""
        if rnd.startswith("data:"):
            try:
                import base64
                from django.core.files.base import ContentFile
                b64 = rnd.split(",", 1)[1]
                oi.render.save(f"order{order.id}_{order.items.count()}.jpg",
                               ContentFile(base64.b64decode(b64)), save=False)
            except Exception:
                pass
        oi.save()
    request.session["cart"] = {}
    has_design = any(i.design for i in order.items.all())
    return render(request, "store/order_success.html", {"order": order, "has_design": has_design})


def order_design_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    pdf = build_order_pdf(order)
    if not pdf:
        messages.info(request, "This order has no custom design to download.")
        return redirect("home")
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="riou-design-order-{order.id}.pdf"'
    return resp


def item_png(request, pk):
    from .models import OrderItem
    it = get_object_or_404(OrderItem, pk=pk)
    if not it.render:
        messages.info(request, "No image available for this item.")
        return redirect("home")
    ext = (it.render.name.rsplit(".", 1)[-1] or "jpg").lower()
    ctype = "image/png" if ext == "png" else "image/jpeg"
    resp = HttpResponse(it.render.read(), content_type=ctype)
    resp["Content-Disposition"] = f'attachment; filename="riou-design-{it.order_id}-{it.id}.{ext}"'
    return resp


def item_pdf(request, pk):
    from .models import OrderItem
    from .pdfgen import build_item_pdf
    it = get_object_or_404(OrderItem, pk=pk)
    pdf = build_item_pdf(it)
    if not pdf:
        messages.info(request, "No design available for this item.")
        return redirect("home")
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="riou-design-{it.order_id}-{it.id}.pdf"'
    return resp
