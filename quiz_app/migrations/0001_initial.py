# Generated by Django 5.1.3 on 2024-11-19 10:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('correct', models.BooleanField(default=False)),
                ('score', models.DecimalField(decimal_places=2, default=1, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answers', models.ManyToManyField(blank=True, to='quiz_app.answer', verbose_name='პასუხები')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizes', to=settings.AUTH_USER_MODEL, verbose_name='შექმნელი')),
                ('questions', models.ManyToManyField(blank=True, to='quiz_app.question', verbose_name='კითხვები')),
            ],
        ),
    ]
