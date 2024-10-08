# Generated by Django 4.2.6 on 2023-10-29 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_customuser_delete_authuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='password',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='datecreated',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='firstname',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='lastname',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
