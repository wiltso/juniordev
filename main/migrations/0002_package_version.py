# Generated by Django 3.0.2 on 2020-01-13 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='version',
            field=models.TextField(default=None, null=True),
        ),
    ]
