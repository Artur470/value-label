# Generated by Django 5.0.6 on 2024-09-21 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_alter_category_value'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='title',
            new_name='label',
        ),
    ]
