# Generated by Django 5.0 on 2024-01-18 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='patient_id',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
