# Generated by Django 5.1.1 on 2024-09-22 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_rename_title_category_label'),
    ]

    operations = [
        migrations.RenameField(
            model_name='color',
            old_name='label',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='color',
            name='value',
        ),
        migrations.AddField(
            model_name='color',
            name='key',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]