# Generated by Django 5.0.1 on 2024-04-09 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salon',
            name='tax_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]