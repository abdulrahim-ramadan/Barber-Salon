# Generated by Django 5.0.1 on 2024-01-24 13:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_ownerprofile_owner'),
        ('contact', '0006_alter_owner_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownerprofile',
            name='owner',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='owner_profile', to='contact.owner', verbose_name='Eigentümer'),
        ),
    ]