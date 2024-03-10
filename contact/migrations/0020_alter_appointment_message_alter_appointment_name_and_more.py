# Generated by Django 5.0.1 on 2024-02-29 17:59

import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0019_remove_appointment_visitor_hash_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='message',
            field=models.TextField(max_length=200, null=True, verbose_name='Nachricht'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='owner',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=15, region=None, verbose_name='Telefon'),
        ),
    ]
