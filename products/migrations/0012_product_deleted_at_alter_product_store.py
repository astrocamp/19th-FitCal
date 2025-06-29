# Generated by Django 5.2.1 on 2025-05-31 08:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_product_price'),
        ('stores', '0008_remove_rating_unique_member_store_store_deleted_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='stores.store'),
        ),
    ]
