# Generated by Django 5.2.1 on 2025-05-22 07:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_merge_20250516_1603'),
        ('stores', '0004_alter_store_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_records', to='members.member')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.store')),
            ],
            options={
                'unique_together': {('member', 'store')},
            },
        ),
        migrations.AddField(
            model_name='member',
            name='favorite',
            field=models.ManyToManyField(related_name='favorited_by', through='members.Favorite', to='stores.store'),
        ),
    ]
