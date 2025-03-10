# Generated by Django 5.1.2 on 2024-12-19 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic_mgt_app', '0003_prescription'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('cost', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Dose',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dose', models.CharField(max_length=255)),
                ('cost', models.FloatField()),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinic_mgt_app.medicine')),
            ],
        ),
    ]
