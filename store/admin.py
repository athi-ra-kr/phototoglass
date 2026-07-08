from django.contrib import admin
from .models import (SiteConfig, Banner, Product, Faq, Lead,
                     ProductCategory, CollectionCategory, Collection, CollectionImage, CollectionDimension,
                     BlogPost, BeforeAfter, CustomerStory, Order, OrderItem)

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("brand", "phone", "whatsapp", "email")

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "active")
    list_editable = ("order", "active")

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active")
    list_editable = ("order", "active")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "product_type", "price", "stock", "active")
    list_editable = ("price", "stock", "active")
    list_filter = ("product_type", "category", "active")
    search_fields = ("name",)

@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("kind", "name", "email", "created")
    list_filter = ("kind",)
    readonly_fields = ("created",)

@admin.register(CollectionCategory)
class CollectionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active")
    list_editable = ("order", "active")

class CollectionImageInline(admin.TabularInline):
    model = CollectionImage
    extra = 3

class CollectionDimensionInline(admin.TabularInline):
    model = CollectionDimension
    extra = 3

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "from_price", "active")
    list_filter = ("category", "active")
    inlines = [CollectionImageInline, CollectionDimensionInline]

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "created")
    list_editable = ("active",)

@admin.register(BeforeAfter)
class BeforeAfterAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "active")
    list_editable = ("order", "active")

@admin.register(CustomerStory)
class CustomerStoryAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "rating", "active")
    list_editable = ("active",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title", "detail", "qty", "unit_price")
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "status", "total", "customer_name")
    list_filter = ("status",)
    list_editable = ("status",)
    readonly_fields = ("created", "total")
    inlines = [OrderItemInline]

# ---- Design Studio Assets ----
from .models import (BackgroundShape, BackgroundShapeDimension, BackgroundImage, BackgroundColor,
                     BackgroundFrame, BackgroundStand, PortraitShape, PortraitImage, PortraitFrame, Embellishment)

class BgDimInline(admin.TabularInline):
    model = BackgroundShapeDimension
    extra = 3

@admin.register(BackgroundShape)
class BackgroundShapeAdmin(admin.ModelAdmin):
    list_display = ("name", "from_price", "order", "active")
    list_editable = ("order", "active")
    inlines = [BgDimInline]

@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active"); list_editable = ("order", "active")

@admin.register(BackgroundColor)
class BackgroundColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "order", "active"); list_editable = ("order", "active")

@admin.register(BackgroundFrame)
class BackgroundFrameAdmin(admin.ModelAdmin):
    list_display = ("name", "shape", "order", "active"); list_filter = ("shape",); list_editable = ("order", "active")

@admin.register(BackgroundStand)
class BackgroundStandAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active"); list_editable = ("order", "active")
    filter_horizontal = ("shapes",)

@admin.register(PortraitShape)
class PortraitShapeAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "order", "active"); list_editable = ("order", "active")

@admin.register(PortraitImage)
class PortraitImageAdmin(admin.ModelAdmin):
    list_display = ("name", "portrait_shape", "dimension", "order", "active"); list_editable = ("order", "active")

@admin.register(PortraitFrame)
class PortraitFrameAdmin(admin.ModelAdmin):
    list_display = ("name", "portrait_shape", "dimension", "order", "active"); list_filter = ("portrait_shape",); list_editable = ("order", "active")

@admin.register(Embellishment)
class EmbellishmentAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active"); list_editable = ("order", "active")

from .models import ProductConfig
@admin.register(ProductConfig)
class ProductConfigAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "price_override", "order", "active")
    list_filter = ("product", "active")
