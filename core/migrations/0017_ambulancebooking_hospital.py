# Generated by Django 5.1.6 on 2025-03-03 09:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_ambulancebooking_pickup_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ambulancebooking',
            name='hospital',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.hospital'),
        ),
    ]
