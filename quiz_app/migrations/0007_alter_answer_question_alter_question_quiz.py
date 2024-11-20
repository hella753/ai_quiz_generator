# Generated by Django 5.1.3 on 2024-11-19 17:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0006_remove_question_answers_remove_quiz_questions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quiz_app.question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz_app.quiz'),
        ),
    ]