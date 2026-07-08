from django.db import models

PRODUCT_TYPE = [("fixed", "Fixed"), ("personalise", "Personalise")]


class SiteConfig(models.Model):
    brand = models.CharField(max_length=80, default="Riou Ocean Glass")
    tagline = models.CharField(max_length=120, default="Printed Glass Studio")
    phone = models.CharField(max_length=40, default="+230 5 123 4567")
    whatsapp = models.CharField(max_length=40, default="23051234567", help_text="Digits only, e.g. 23051234567")
    email = models.EmailField(default="hello@riouoceanglass.mu")
    address = models.TextField(default="Royal Road, Curepipe, Mauritius")
    map_embed = models.URLField(blank=True, default="https://www.google.com/maps?q=Mauritius&output=embed",
                                help_text="Google Maps embed URL (Share → Embed a map → copy the src)")
    facebook = models.URLField(blank=True, default="https://facebook.com")
    instagram = models.URLField(blank=True, default="https://instagram.com")
    tiktok = models.URLField(blank=True, default="https://tiktok.com")
    youtube = models.URLField(blank=True, default="https://youtube.com")
    logo_light = models.ImageField(upload_to="logo/", blank=True, null=True, help_text="Logo for LIGHT mode (PNG, transparent background)")
    logo_dark = models.ImageField(upload_to="logo/", blank=True, null=True, help_text="Logo for DARK mode (PNG, transparent background)")
    favicon = models.ImageField(upload_to="logo/", blank=True, null=True, help_text="Browser tab icon (square PNG, e.g. 512×512)")

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return self.brand

    @classmethod
    def get(cls):
        return cls.objects.first() or cls.objects.create()


class Banner(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="banners/", blank=True, null=True,
                              help_text="Right-side image (no text baked in — text comes from the fields above)")
    gradient = models.CharField(max_length=200, default="linear-gradient(135deg,#04323b,#0e7d8a 55%,#7fd6c9)",
                                help_text="Fallback background if no image is uploaded")
    btn1_text = models.CharField(max_length=40, blank=True, default="Design yours now")
    btn1_link = models.CharField(max_length=200, blank=True, default="/studio/", help_text="Path or URL, e.g. /studio/")
    btn2_text = models.CharField(max_length=40, blank=True, default="Browse collections")
    btn2_link = models.CharField(max_length=200, blank=True, default="/collections/")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class ProductCategory(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Product category"
        verbose_name_plural = "Product categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    product_type = models.CharField(max_length=12, choices=PRODUCT_TYPE, default="fixed",
                                    help_text="Fixed: buy directly. Personalise: customer must use the studio (configs); no direct Add to cart.")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    motif = models.CharField(max_length=8, default="🌊")
    gradient = models.CharField(max_length=200, default="linear-gradient(135deg,#0a4f5c,#7fd6c9)")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def type_label(self):
        return self.get_product_type_display()

    @property
    def is_personalise(self):
        return self.product_type == "personalise"

    @property
    def category_name(self):
        return self.category.name if self.category else ""

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"

    def __str__(self):
        return self.question


class Lead(models.Model):
    KIND = [("quote", "B2B quote"), ("contact", "Contact message")]
    kind = models.CharField(max_length=10, choices=KIND, default="contact")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=120, blank=True)
    segment = models.CharField(max_length=80, blank=True)
    quantity = models.CharField(max_length=40, blank=True)
    message = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.name}"


# ---------- Collections (category -> collection -> images + dimensions) ----------
class CollectionCategory(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Collection category"
        verbose_name_plural = "Collection categories"

    def __str__(self):
        return self.name


class Collection(models.Model):
    category = models.ForeignKey(CollectionCategory, on_delete=models.CASCADE, related_name="collections")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    @property
    def cover(self):
        return self.images.first()

    @property
    def thumb_url(self):
        c = self.cover
        return c.image.url if c else ""

    @property
    def from_price(self):
        d = self.dimensions.order_by("price").first()
        return d.price if d else None


class CollectionImage(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="collections/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image #{self.pk}"


class CollectionDimension(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="dimensions")
    width_cm = models.PositiveIntegerField()
    height_cm = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["price"]

    @property
    def label(self):
        return f"{self.width_cm} × {self.height_cm} cm"

    def __str__(self):
        return f"{self.label} · €{self.price}"


# ---------- Inspiration ----------
class BlogPost(models.Model):
    title = models.CharField(max_length=160)
    excerpt = models.CharField(max_length=200, help_text="One-line summary shown on the card")
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    body = models.TextField(help_text="Supports **bold**, *italic*, blank-line paragraphs and '- ' bullet lists")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class BeforeAfter(models.Model):
    title = models.CharField(max_length=120)
    caption = models.CharField(max_length=200, blank=True)
    before_image = models.ImageField(upload_to="beforeafter/")
    after_image = models.ImageField(upload_to="beforeafter/")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Before / after"
        verbose_name_plural = "Before / after"

    def __str__(self):
        return self.title

    @property
    def thumb_url(self):
        return self.after_image.url if self.after_image else ""


class CustomerStory(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="stories/", blank=True, null=True)
    youtube_url = models.URLField(blank=True, help_text="Full YouTube link (optional)")
    story = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Customer story"
        verbose_name_plural = "Customer stories"

    def __str__(self):
        return f"{self.name}"

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""

    @property
    def youtube_embed(self):
        u = self.youtube_url
        if not u:
            return ""
        vid = ""
        if "watch?v=" in u:
            vid = u.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in u:
            vid = u.split("youtu.be/")[1].split("?")[0]
        elif "embed/" in u:
            vid = u.split("embed/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{vid}" if vid else ""


# ---------- Orders ----------
class Order(models.Model):
    STATUS = [("received", "Received"), ("processing", "Processing"), ("done", "Completed")]
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS, default="received")
    customer_name = models.CharField(max_length=120, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.pk} · €{self.total}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=160)
    detail = models.CharField(max_length=120, blank=True)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    design = models.JSONField(blank=True, null=True)
    render = models.ImageField(upload_to="orders/", blank=True, null=True)

    @property
    def line_total(self):
        return self.unit_price * self.qty

    def __str__(self):
        return f"{self.title} ×{self.qty}"


# ================= Design Studio Assets =================
class BackgroundShape(models.Model):
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def from_price(self):
        d = self.dimensions.order_by("base_price").first()
        return d.base_price if d else None


class BackgroundShapeDimension(models.Model):
    shape = models.ForeignKey(BackgroundShape, on_delete=models.CASCADE, related_name="dimensions")
    width_cm = models.PositiveIntegerField()
    height_cm = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Base price for this shape at this size")

    class Meta:
        ordering = ["base_price"]

    @property
    def label(self):
        return f"{self.width_cm} × {self.height_cm} cm"

    def __str__(self):
        return f"{self.shape.name} · {self.label}"


class BackgroundImage(models.Model):
    name = models.CharField(max_length=80)
    shape = models.ForeignKey(BackgroundShape, on_delete=models.CASCADE, related_name="bg_images", null=True, blank=True,
                              help_text="Set automatically from the chosen size")
    dimension = models.ForeignKey(BackgroundShapeDimension, on_delete=models.CASCADE, related_name="bg_images",
                                  help_text="The exact size this image is made for")
    image = models.ImageField(upload_to="studio/backgrounds/")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.dimension_id:
            self.shape_id = self.dimension.shape_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class BackgroundColor(models.Model):
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=200, help_text="A CSS color or gradient, e.g. #0a4f5c or linear-gradient(...)")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class BackgroundFrame(models.Model):
    shape = models.ForeignKey(BackgroundShape, on_delete=models.CASCADE, related_name="frames", null=True, blank=True,
                              help_text="Set automatically from the chosen size")
    dimension = models.ForeignKey(BackgroundShapeDimension, on_delete=models.CASCADE, related_name="frames",
                                  help_text="The exact size this frame is made for")
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to="studio/bgframes/", help_text="Frame graphic (transparent centre)")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.dimension_id:
            self.shape_id = self.dimension.shape_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.dimension.label}" if self.dimension_id else self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class BackgroundStand(models.Model):
    """A physical stand/easel photo. Admin ticks which Background Shape(s) it fits."""
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to="studio/bgstands/", help_text="Photo of the stand")
    shapes = models.ManyToManyField(BackgroundShape, related_name="stands", blank=True,
                                    help_text="Tick every Background Shape this stand fits")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class PortraitShape(models.Model):
    KEYS = [("square", "Square"), ("heart", "Heart"), ("circle", "Circle"),
            ("topwave", "Top wave"), ("oval", "Oval")]
    name = models.CharField(max_length=80)
    key = models.CharField(max_length=20, choices=KEYS, default="square",
                           help_text="Coded outline used to cut the photo (fixed in code)")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class PortraitShapeDimension(models.Model):
    shape = models.ForeignKey(PortraitShape, on_delete=models.CASCADE, related_name="dimensions")
    width_cm = models.DecimalField(max_digits=6, decimal_places=1)
    height_cm = models.DecimalField(max_digits=6, decimal_places=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    @property
    def label(self):
        def f(v):
            v = float(v)
            return str(int(v)) if v == int(v) else str(v)
        return f"{f(self.width_cm)} × {f(self.height_cm)} cm"

    def __str__(self):
        return f"{self.shape.name} · {self.label}"


class PortraitImage(models.Model):
    name = models.CharField(max_length=80)
    portrait_shape = models.ForeignKey(PortraitShape, on_delete=models.CASCADE, related_name="images", null=True, blank=True,
                                       help_text="Set automatically from the chosen size")
    dimension = models.ForeignKey(PortraitShapeDimension, on_delete=models.CASCADE, related_name="images",
                                  help_text="The portrait shape + size this image is made for")
    image = models.ImageField(upload_to="studio/portraitimages/")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.dimension_id:
            self.portrait_shape_id = self.dimension.shape_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class PortraitFrame(models.Model):
    portrait_shape = models.ForeignKey(PortraitShape, on_delete=models.CASCADE, related_name="frames", null=True, blank=True,
                                       help_text="Set automatically from the chosen size")
    dimension = models.ForeignKey(PortraitShapeDimension, on_delete=models.CASCADE, related_name="frames",
                                  help_text="The portrait shape + size this frame is made for")
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to="studio/portraitframes/")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.dimension_id:
            self.portrait_shape_id = self.dimension.shape_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.dimension.label}" if self.dimension_id else self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


class Embellishment(models.Model):
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to="studio/stickers/")
    width = models.PositiveIntegerField(default=70, help_text="Default on-canvas width (px)")
    height = models.PositiveIntegerField(default=70, help_text="Default on-canvas height (px)")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Embellishment / sticker"

    def __str__(self):
        return self.name

    @property
    def thumb_url(self):
        return self.image.url if self.image else ""


# ================= Product configurations (admin-built designs) =================
class ProductConfig(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="configs")
    name = models.CharField(max_length=120, default="Configuration")
    design = models.JSONField(blank=True, null=True, help_text="Serialized studio design")
    price_override = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                         help_text="Optional fixed price (else the shape/size base price applies)")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} · {self.name}"

    @property
    def thumb_url(self):
        return self.product.thumb_url
