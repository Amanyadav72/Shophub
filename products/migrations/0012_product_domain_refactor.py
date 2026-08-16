from django.conf import settings
from django.db import migrations, models


def assign_orphaned_products(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    orphaned = Product.objects.filter(owner__isnull=True)
    if not orphaned.exists():
        return
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    fallback_owner = User.objects.filter(is_superuser=True).order_by("id").first()
    if fallback_owner is None:
        raise RuntimeError("A superuser is required before migrating orphaned products.")
    orphaned.update(owner=fallback_owner)


class Migration(migrations.Migration):
    dependencies = [("products", "0011_alter_product_options")]

    operations = [
        migrations.RunPython(assign_orphaned_products, migrations.RunPython.noop),
        migrations.AlterField(model_name="product", name="owner", field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="products", to=settings.AUTH_USER_MODEL)),
        migrations.AlterField(model_name="product", name="stock", field=models.PositiveIntegerField(default=0)),
        migrations.AlterField(model_name="product", name="is_available", field=models.BooleanField(default=False, editable=False)),
        migrations.AlterField(model_name="sellerprofile", name="phone", field=models.CharField(blank=True, max_length=15)),
        migrations.AlterField(model_name="sellerprofile", name="address", field=models.TextField(blank=True)),
    ]
