# Generated by Django 4.2.6 on 2023-10-29 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_alter_customuser_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='datecreated',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_staff',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
    ]
