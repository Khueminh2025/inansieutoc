# Generated by Django 5.2.4 on 2025-07-26 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_order_options_remove_order_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='laminate',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shape',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
