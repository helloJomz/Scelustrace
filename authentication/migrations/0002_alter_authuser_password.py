# Generated by Django 4.2.6 on 2023-10-14 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='password',
            field=models.CharField(max_length=150),
        ),
    ]
