# Generated by Django 5.2.1 on 2025-06-05 18:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0009_store_cover_image_store_logo_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='stores.store')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('store', 'name'), name='unique_category_store')],
            },
        ),
    ]
