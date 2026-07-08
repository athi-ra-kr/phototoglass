from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelform_factory
from django.contrib import messages
from django.urls import reverse
from django import forms as dj_forms
from .models import (Banner, Product, Faq, Lead, SiteConfig, ProductCategory, CollectionCategory,
                     Collection, CollectionImage, CollectionDimension,
                     BlogPost, BeforeAfter, CustomerStory, Order,
                     BackgroundShape, BackgroundShapeDimension, BackgroundImage, BackgroundColor,
                     BackgroundFrame, BackgroundStand, PortraitShape, PortraitImage, PortraitFrame, Embellishment, ProductConfig)

# simple, single-record models managed by the generic editor
REGISTRY = {
    "banners":     {"model": Banner,             "label": "Banners",    "icon": "🖼️",
                    "fields": ["title", "description", "image", "gradient", "btn1_text", "btn1_link", "btn2_text", "btn2_link", "order", "active"]},
    "productcats": {"model": ProductCategory,    "label": "Product categories", "icon": "🏷️",
                    "fields": ["name", "description", "order", "active"]},
    "products":    {"model": Product,            "label": "Products",   "icon": "🧊",
                    "fields": ["name", "category", "product_type", "price", "image", "description", "stock", "active", "order"]},
    "categories":  {"model": CollectionCategory, "label": "Collection categories", "icon": "🗂️",
                    "fields": ["name", "description", "order", "active"]},
    "blog":        {"model": BlogPost,           "label": "Blog / Tips", "icon": "📝",
                    "fields": ["title", "excerpt", "image", "body", "active"]},
    "beforeafter": {"model": BeforeAfter,        "label": "Before / After", "icon": "🔀",
                    "fields": ["title", "caption", "before_image", "after_image", "order", "active"]},
    "stories":     {"model": CustomerStory,      "label": "Customer Stories", "icon": "⭐",
                    "fields": ["name", "location", "image", "youtube_url", "story", "rating", "order", "active"]},
    "faqs":        {"model": Faq,                "label": "FAQ",        "icon": "❓",
                    "fields": ["question", "answer", "order"]},
    "bgimages":      {"model": BackgroundImage, "label": "Background Images", "icon": "🌅",
                     "fields": ["dimension", "name", "image", "order", "active"]},
    "bgcolors":      {"model": BackgroundColor, "label": "Background Colors", "icon": "🟦",
                     "fields": ["name", "color", "order", "active"]},
    "bgframes":      {"model": BackgroundFrame, "label": "Background Frames", "icon": "🔲",
                     "fields": ["dimension", "name", "image", "order", "active"]},
    "portraitimages":{"model": PortraitImage, "label": "Portrait Images", "icon": "🖼️",
                     "fields": ["dimension", "name", "image", "order", "active"]},
    "portraitframes":{"model": PortraitFrame, "label": "Portrait Frames", "icon": "🔳",
                     "fields": ["dimension", "name", "image", "order", "active"]},
    "stickers":      {"model": Embellishment, "label": "Embellishments", "icon": "✨",
                     "fields": ["name", "image", "width", "height", "order", "active"]},
    "bgstands":      {"model": BackgroundStand, "label": "Background Stands", "icon": "🧍",
                     "fields": ["name", "image", "shapes", "order", "active"],
                     "widgets": {"shapes": dj_forms.CheckboxSelectMultiple}},
}

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="dash_login")


def _nav(active=None):
    def reg(k):
        v = REGISTRY[k]
        return {"label": v["label"], "icon": v["icon"], "href": reverse("dash_list", args=[k]), "active": active == k}
    items = [{"label": "Overview", "icon": "📊", "href": reverse("dash"), "active": active == "overview"}]
    items += [reg("banners"), reg("productcats"), reg("products"), reg("categories")]
    items.append({"label": "Collections", "icon": "🎨", "href": reverse("dash_collections"), "active": active == "collections"})
    items += [reg("blog"), reg("beforeafter"), reg("stories"), reg("faqs")]
    asset_keys = {"shapes", "bgimages", "bgcolors", "bgframes", "bgstands", "pshapes", "portraitimages", "portraitframes", "stickers"}
    assets = [{"label": "Background Shapes", "icon": "🟩", "href": reverse("dash_shapes"), "active": active == "shapes"}]
    assets += [reg("bgimages"), reg("bgcolors"), reg("bgframes"), reg("bgstands")]
    assets += [{"label": "Portrait Shapes", "icon": "🔷", "href": reverse("dash_pshapes"), "active": active == "pshapes"}]
    assets += [reg("portraitimages"), reg("portraitframes"), reg("stickers")]
    items.append({"group": True, "label": "Design assets", "icon": "🎨", "active": active in asset_keys, "children": assets})
    items.append({"label": "Orders", "icon": "🧾", "href": reverse("dash_orders"), "active": active == "orders"})
    items.append({"label": "Leads", "icon": "📥", "href": reverse("dash_leads"), "active": active == "leads"})
    items.append({"label": "Site config", "icon": "⚙️", "href": reverse("dash_site"), "active": active == "site"})
    return items


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dash")
    error = None
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid() and form.get_user().is_staff:
            login(request, form.get_user())
            return redirect(request.GET.get("next") or "dash")
        error = "Invalid credentials or no dashboard access."
    else:
        form = AuthenticationForm()
    return render(request, "dashboard/login.html", {"form": form, "error": error})


def logout_view(request):
    logout(request)
    return redirect("dash_login")


@staff_required
def overview(request):
    stats = [{"key": k, "label": v["label"], "icon": v["icon"], "count": v["model"].objects.count()}
             for k, v in REGISTRY.items()]
    stats.append({"key": "collections", "label": "Collections", "icon": "🎨", "count": Collection.objects.count()})
    stats.append({"key": "orders", "label": "Orders", "icon": "🧾", "count": Order.objects.count()})
    stats.append({"key": "shapes", "label": "Background Shapes", "icon": "🟩", "count": BackgroundShape.objects.count()})
    return render(request, "dashboard/overview.html",
                  {"stats": stats, "nav": _nav("overview"), "leads": Lead.objects.count()})


@staff_required
def listing(request, key):
    if key not in REGISTRY:
        return redirect("dash")
    cfg = REGISTRY[key]
    return render(request, "dashboard/list.html",
                  {"objects": cfg["model"].objects.all(), "cfg": cfg, "key": key, "nav": _nav(key)})


@staff_required
def edit(request, key, pk=None):
    if key not in REGISTRY:
        return redirect("dash")
    cfg = REGISTRY[key]
    Model = cfg["model"]
    instance = get_object_or_404(Model, pk=pk) if pk else None
    Form = modelform_factory(Model, fields=cfg["fields"], widgets=cfg.get("widgets"))
    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"{cfg['label']} saved.")
            return redirect("dash_list", key=key)
    else:
        form = Form(instance=instance)
    return render(request, "dashboard/form.html",
                  {"form": form, "cfg": cfg, "key": key, "instance": instance, "nav": _nav(key)})


@staff_required
def delete(request, key, pk):
    if key not in REGISTRY:
        return redirect("dash")
    cfg = REGISTRY[key]
    obj = get_object_or_404(cfg["model"], pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Deleted.")
        return redirect("dash_list", key=key)
    return render(request, "dashboard/delete.html", {"obj": obj, "cfg": cfg, "key": key,
                                                     "cancel": reverse("dash_list", args=[key]), "nav": _nav(key)})


# ---------- Collections (custom: base fields + images + dimensions) ----------
CollectionForm = modelform_factory(Collection, fields=["category", "title", "description", "active"])

@staff_required
def collection_list(request):
    return render(request, "dashboard/collection_list.html",
                  {"objects": Collection.objects.all(), "nav": _nav("collections")})

@staff_required
def collection_edit(request, pk=None):
    col = get_object_or_404(Collection, pk=pk) if pk else None
    if request.method == "POST":
        form = CollectionForm(request.POST, instance=col)
        if form.is_valid():
            col = form.save()
            # new images
            for f in request.FILES.getlist("new_images"):
                CollectionImage.objects.create(collection=col, image=f)
            # new dimension rows
            ws = request.POST.getlist("dim_w"); hs = request.POST.getlist("dim_h")
            ps = request.POST.getlist("dim_price"); ss = request.POST.getlist("dim_stock")
            for w, h, p, s in zip(ws, hs, ps, ss):
                if w and h and p:
                    try:
                        CollectionDimension.objects.create(
                            collection=col, width_cm=int(w), height_cm=int(h),
                            price=Decimal(p), stock=int(s or 0))
                    except (ValueError, InvalidOperation):
                        pass
            messages.success(request, "Collection saved.")
            return redirect("dash_collection_edit", pk=col.pk)
    else:
        form = CollectionForm(instance=col)
    return render(request, "dashboard/collection_form.html",
                  {"form": form, "col": col, "nav": _nav("collections")})

@staff_required
def collection_delete(request, pk):
    col = get_object_or_404(Collection, pk=pk)
    if request.method == "POST":
        col.delete()
        messages.success(request, "Collection deleted.")
        return redirect("dash_collections")
    return render(request, "dashboard/delete.html",
                  {"obj": col, "cfg": {"label": "Collection"}, "cancel": reverse("dash_collections"), "nav": _nav("collections")})

@staff_required
def collimage_delete(request, pk):
    img = get_object_or_404(CollectionImage, pk=pk); cid = img.collection_id; img.delete()
    return redirect("dash_collection_edit", pk=cid)

@staff_required
def colldim_delete(request, pk):
    d = get_object_or_404(CollectionDimension, pk=pk); cid = d.collection_id; d.delete()
    return redirect("dash_collection_edit", pk=cid)


# ---------- Orders & leads ----------
@staff_required
def orders(request):
    return render(request, "dashboard/orders.html", {"orders": Order.objects.all(), "nav": _nav("orders")})

@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.status = request.POST.get("status", order.status); order.save()
        messages.success(request, "Order updated.")
        return redirect("dash_order", pk=pk)
    return render(request, "dashboard/order_detail.html", {"order": order, "nav": _nav("orders")})

@staff_required
def leads(request):
    return render(request, "dashboard/leads.html", {"leads": Lead.objects.all(), "nav": _nav("leads")})

@staff_required
def site_config(request):
    obj = SiteConfig.get()
    Form = modelform_factory(SiteConfig, fields=["brand", "tagline", "phone", "whatsapp", "email", "address", "map_embed", "facebook", "instagram", "tiktok", "youtube", "logo_light", "logo_dark", "favicon"])
    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save(); messages.success(request, "Site configuration saved.")
            return redirect("dash_site")
    else:
        form = Form(instance=obj)
    return render(request, "dashboard/form.html",
                  {"form": form, "cfg": {"label": "Site configuration"}, "key": "site", "instance": obj, "nav": _nav("site"), "is_site": True})


# ---------- Background Shapes (fixed shapes; admin edits dimension prices only) ----------
@staff_required
def shape_list(request):
    if request.method == "POST":
        for d in BackgroundShapeDimension.objects.all():
            v = request.POST.get(f"price_{d.id}")
            if v:
                try:
                    d.base_price = Decimal(v); d.save()
                except (ValueError, InvalidOperation):
                    pass
        messages.success(request, "Prices updated.")
        return redirect("dash_shapes")
    return render(request, "dashboard/shape_list.html",
                  {"shapes": BackgroundShape.objects.all(), "nav": _nav("shapes")})


# ---------- Product configurations ----------
@staff_required
def product_configs(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not product.is_personalise:
        messages.info(request, "This product is Fixed — it doesn't use configurations. Switch it to Personalise first.")
        return redirect("dash_list", key="products")
    return render(request, "dashboard/product_configs.html",
                  {"product": product, "configs": product.configs.all(), "nav": _nav("products")})

@staff_required
def config_delete(request, pk):
    cfg = get_object_or_404(ProductConfig, pk=pk); pid = cfg.product_id
    if request.method == "POST":
        cfg.delete(); messages.success(request, "Configuration deleted.")
        return redirect("dash_product_configs", pk=pid)
    return render(request, "dashboard/delete.html",
                  {"obj": cfg, "cfg": {"label": "Configuration"},
                   "cancel": reverse("dash_product_configs", args=[pid]), "nav": _nav("products")})


ConfigForm = modelform_factory(ProductConfig, fields=["name", "price_override", "active", "order"])

@staff_required
def config_edit(request, pk):
    cfg = get_object_or_404(ProductConfig, pk=pk)
    if request.method == "POST":
        form = ConfigForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save(); messages.success(request, "Configuration updated.")
            return redirect("dash_product_configs", pk=cfg.product_id)
    else:
        form = ConfigForm(instance=cfg)
    return render(request, "dashboard/config_form.html", {"form": form, "cfg_obj": cfg, "nav": _nav("products")})


@staff_required
def portrait_shapes(request):
    shapes = PortraitShape.objects.all().prefetch_related("dimensions")
    return render(request, "dashboard/portrait_shapes.html",
                  {"nav": _nav("pshapes"), "shapes": shapes})
