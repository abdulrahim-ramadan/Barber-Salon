# Generated by Django 5.0.1 on 2024-01-18 02:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('contact', '0004_galleryitem_user_alter_appointment_barber'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='barber',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barber_profile', to='contact.barber', verbose_name='Friseur'),
        ),
    ]