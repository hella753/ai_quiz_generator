# Generated by Django 5.1.3 on 2024-11-23 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_delete_customanonymoususer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 20 character or fewer.', max_length=20, unique=True, verbose_name='username'),
        ),
    ]
