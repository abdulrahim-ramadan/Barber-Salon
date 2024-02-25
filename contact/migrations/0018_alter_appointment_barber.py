# Generated by Django 5.0.1 on 2024-02-19 09:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0017_remove_appointment_visitor_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='barber',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barber_appointment', to='contact.barber', verbose_name='Friseur'),
        ),
    ]