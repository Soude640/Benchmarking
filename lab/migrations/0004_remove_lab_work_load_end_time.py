# Generated by Django 4.1.7 on 2023-03-01 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0003_lab_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lab',
            name='work_load_end_time',
        ),
    ]
