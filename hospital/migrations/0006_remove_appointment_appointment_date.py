# Generated by Django 5.0 on 2024-01-18 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0005_remove_userdetails_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='appointment_date',
        ),
    ]
