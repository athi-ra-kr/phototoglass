# Hand-edited to be safe on a LIVE database that may already have real FrameStand
# rows (name + photo, entered by the admin). This RENAMES the model (preserving those
# rows) instead of deleting FrameStand and creating a brand new empty BackgroundStand.
# The old `frames` (M2M to BackgroundFrame) is dropped and a new `shapes` (M2M to
# BackgroundShape) is added — that relationship is genuinely different, so any frame
# ticks the admin made are reset (expected; there's no way to auto-infer shapes from
# frames), but the stand's name/photo/order/active are kept intact.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_frame_stand_and_product_type'),
    ]

    operations = [
        migrations.RenameModel(old_name='FrameStand', new_name='BackgroundStand'),
        migrations.AlterField(
            model_name='backgroundstand',
            name='image',
            field=models.ImageField(help_text='Photo of the stand', upload_to='studio/bgstands/'),
        ),
        migrations.RemoveField(
            model_name='backgroundstand',
            name='frames',
        ),
        migrations.AddField(
            model_name='backgroundstand',
            name='shapes',
            field=models.ManyToManyField(blank=True, help_text='Tick every Background Shape this stand fits', related_name='stands', to='store.backgroundshape'),
        ),
    ]
