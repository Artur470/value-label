# Generated by Django 5.0.6 on 2024-09-21 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_product_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='value',
            field=models.CharField(default=1, editable=False, max_length=200),
            preserve_default=False,
        ),
    ]
