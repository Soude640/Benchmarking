# Generated by Django 4.1.7 on 2023-03-01 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0002_lab_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]