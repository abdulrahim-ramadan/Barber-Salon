# Generated by Django 5.0.1 on 2024-03-10 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0027_remove_service_product_alter_product_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='service',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_service', to='contact.service'),
        ),
    ]
