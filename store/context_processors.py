import os
from django.conf import settings
from django.urls import reverse
from .models import SiteConfig, CollectionCategory, ProductCategory

def site(request):
    cart = request.session.get("cart", {})
    count = sum(i.get("qty", 0) for i in cart.values()) if cart else 0

    pcats = ProductCategory.objects.filter(active=True)
    ccats = CollectionCategory.objects.filter(active=True)
    nav = [
        {"key": "home", "label": "Home", "href": reverse("home")},
        {"key": "products", "label": "Products", "href": reverse("products"),
         "children": [{"label": c.name, "href": reverse("product_category", args=[c.id])} for c in pcats]
                     + [{"label": "Design Yourself", "href": reverse("studio")}]},
        {"key": "collections", "label": "Collections", "href": reverse("collections"),
         "children": [{"label": c.name, "href": reverse("category", args=[c.id])} for c in ccats]},
        {"key": "b2b", "label": "B2B", "href": reverse("b2b")},
        {"key": "inspiration", "label": "Inspiration", "href": reverse("inspiration"), "children": [
            {"label": "Blog / Tips", "href": reverse("blog")},
            {"label": "Before & After Gallery", "href": reverse("before_after")},
            {"label": "Size Guide", "href": reverse("size_guide")},
            {"label": "Photo Preparation Guide", "href": reverse("photo_guide")},
            {"label": "Customer Stories", "href": reverse("customer_stories")},
        ]},
        {"key": "howitworks", "label": "How It Works", "href": reverse("howitworks")},
        {"key": "about", "label": "About", "href": reverse("about")},
        {"key": "contact", "label": "Contact", "href": reverse("contact")},
    ]

    sc = SiteConfig.get()

    def _asset(field, legacy_name):
        f = getattr(sc, field, None)
        if f:
            try:
                return True, f.url
            except Exception:
                pass
        p = os.path.join(settings.MEDIA_ROOT, "logo", legacy_name)
        if os.path.exists(p):
            return True, settings.MEDIA_URL + "logo/" + legacy_name
        return False, ""

    has_light, light_url = _asset("logo_light", "logo.png")
    has_dark, dark_url = _asset("logo_dark", "logo2.png")
    has_fav, fav_url = _asset("favicon", "favicon.png")

    return {"NAV": nav, "SITE": sc, "cart_count": count,
            "HAS_FAVICON": has_fav,
            "FAVICON_URL": fav_url,
            "HAS_LOGO": has_light or has_dark,
            "HAS_LOGO_LIGHT": has_light, "HAS_LOGO_DARK": has_dark,
            "LOGO_LIGHT_URL": light_url,
            "LOGO_DARK_URL": dark_url}
