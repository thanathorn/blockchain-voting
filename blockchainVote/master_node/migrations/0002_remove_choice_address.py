# Generated by Django 3.2.3 on 2021-05-23 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_node', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice',
            name='address',
        ),
    ]
