# Generated by Django 4.2.2 on 2023-07-05 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_alter_listing_list_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='list_user',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Listing User'),
        ),
    ]
