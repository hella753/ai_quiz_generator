# Generated by Django 5.1.3 on 2025-03-02 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_verificationtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, unique=True, verbose_name='email'),
        ),
    ]