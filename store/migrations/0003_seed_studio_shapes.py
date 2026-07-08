from decimal import Decimal
from django.db import migrations

# Canonical, developer-defined studio shapes. Edit/extend here and ship a NEW
# migration for any future change — `python manage.py migrate` then applies it
# automatically and idempotently, with no `seed` and no risk to existing data.

BG_SHAPES = [
    # name, order, [(width_cm, height_cm, base_price), ...]
    ("Rectangle Landscape", 0, [(35, 25, "49"), (50, 35, "69"), (60, 40, "89"), (85, 60, "129")]),
    ("Rectangle Portrait", 1, [(25, 35, "49"), (35, 50, "69"), (40, 60, "89"), (60, 85, "129")]),
]

PORTRAIT_SHAPES = [
    # name, key (coded outline), order, (width_cm, height_cm)
    ("Square", "square", 0, (8, 8)),
    ("Heart", "heart", 1, (9, 9)),
    ("Circle", "circle", 2, (8, 8)),
    ("Oval", "oval", 3, (8, 12)),
]


def seed_shapes(apps, schema_editor):
    BackgroundShape = apps.get_model("store", "BackgroundShape")
    BackgroundShapeDimension = apps.get_model("store", "BackgroundShapeDimension")
    PortraitShape = apps.get_model("store", "PortraitShape")
    PortraitShapeDimension = apps.get_model("store", "PortraitShapeDimension")

    for name, order, dims in BG_SHAPES:
        sh, _ = BackgroundShape.objects.get_or_create(name=name, defaults={"order": order, "active": True})
        for w, h, price in dims:
            BackgroundShapeDimension.objects.get_or_create(
                shape=sh, width_cm=Decimal(str(w)), height_cm=Decimal(str(h)),
                defaults={"base_price": Decimal(price)},
            )

    for name, key, order, (w, h) in PORTRAIT_SHAPES:
        ps, created = PortraitShape.objects.get_or_create(name=name, defaults={"key": key, "order": order, "active": True})
        if ps.key != key:  # keep the coded outline correct
            ps.key = key
            ps.save(update_fields=["key"])
        PortraitShapeDimension.objects.get_or_create(
            shape=ps, width_cm=Decimal(str(w)), height_cm=Decimal(str(h)),
            defaults={"order": 0},
        )


def unseed(apps, schema_editor):
    # Intentionally keep the data on reverse so we never destroy shapes that
    # existing orders/configs may reference.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_siteconfig_favicon_siteconfig_logo_dark_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_shapes, unseed),
    ]
