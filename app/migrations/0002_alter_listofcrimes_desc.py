# Generated by Django 4.2.6 on 2023-10-29 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listofcrimes',
            name='desc',
            field=models.CharField(default=None, max_length=500),
        ),
    ]
