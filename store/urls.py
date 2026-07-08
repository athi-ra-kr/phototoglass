from django.urls import path
from . import views, dashboard

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("products/category/<int:pk>/", views.products_category, name="product_category"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    path("collections/", views.collections, name="collections"),
    path("collections/<int:pk>/", views.category, name="category"),
    path("collection/<int:pk>/", views.collection_detail, name="collection_detail"),

    path("b2b/", views.b2b, name="b2b"),

    path("inspiration/", views.inspiration, name="inspiration"),
    path("inspiration/blog/", views.blog, name="blog"),
    path("inspiration/blog/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("inspiration/before-after/", views.before_after, name="before_after"),
    path("inspiration/size-guide/", views.size_guide, name="size_guide"),
    path("inspiration/photo-guide/", views.photo_guide, name="photo_guide"),
    path("inspiration/customer-stories/", views.customer_stories, name="customer_stories"),

    path("how-it-works/", views.howitworks, name="howitworks"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("account/", views.account, name="account"),
    path("studio/", views.studio, name="studio"),
    path("api/studio/assets/", views.studio_assets, name="studio_assets"),
    path("studio/add/", views.studio_add, name="studio_add"),
    path("studio/save-config/", views.studio_save_config, name="studio_save_config"),

    path("cart/", views.cart, name="cart"),
    path("cart/remove/<str:key>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:pk>/design.pdf", views.order_design_pdf, name="order_design_pdf"),
    path("item/<int:pk>/design.png", views.item_png, name="item_png"),
    path("item/<int:pk>/design.pdf", views.item_pdf, name="item_pdf"),

    # ---- staff dashboard ----
    path("dashboard/login/", dashboard.login_view, name="dash_login"),
    path("dashboard/logout/", dashboard.logout_view, name="dash_logout"),
    path("dashboard/", dashboard.overview, name="dash"),
    path("dashboard/site/", dashboard.site_config, name="dash_site"),
    path("dashboard/leads/", dashboard.leads, name="dash_leads"),
    path("dashboard/orders/", dashboard.orders, name="dash_orders"),
    path("dashboard/orders/<int:pk>/", dashboard.order_detail, name="dash_order"),
    # collections (custom: images + dimensions)
    path("dashboard/collections/", dashboard.collection_list, name="dash_collections"),
    path("dashboard/collections/new/", dashboard.collection_edit, name="dash_collection_new"),
    path("dashboard/collections/<int:pk>/edit/", dashboard.collection_edit, name="dash_collection_edit"),
    path("dashboard/collections/<int:pk>/delete/", dashboard.collection_delete, name="dash_collection_delete"),
    path("dashboard/collimage/<int:pk>/delete/", dashboard.collimage_delete, name="dash_collimage_delete"),
    path("dashboard/colldim/<int:pk>/delete/", dashboard.colldim_delete, name="dash_colldim_delete"),
    # background shapes (fixed; price-only editor)
    path("dashboard/shapes/", dashboard.shape_list, name="dash_shapes"),
    path("dashboard/portrait-shapes/", dashboard.portrait_shapes, name="dash_pshapes"),
    # product configurations
    path("dashboard/products/<int:pk>/configs/", dashboard.product_configs, name="dash_product_configs"),
    path("dashboard/config/<int:pk>/edit/", dashboard.config_edit, name="dash_config_edit"),
    path("dashboard/config/<int:pk>/delete/", dashboard.config_delete, name="dash_config_delete"),
    # generic simple models
    path("dashboard/<str:key>/", dashboard.listing, name="dash_list"),
    path("dashboard/<str:key>/new/", dashboard.edit, name="dash_new"),
    path("dashboard/<str:key>/<int:pk>/edit/", dashboard.edit, name="dash_edit"),
    path("dashboard/<str:key>/<int:pk>/delete/", dashboard.delete, name="dash_delete"),
]
