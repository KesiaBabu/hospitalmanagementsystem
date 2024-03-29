# Generated by Django 5.0 on 2024-01-18 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_name', models.CharField(max_length=255, null=True)),
                ('patient_address', models.CharField(max_length=255, null=True)),
                ('mobile_number', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
