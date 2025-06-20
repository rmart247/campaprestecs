# Generated by Django 5.2.1 on 2025-06-15 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaprestecs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuari',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='usuari',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
