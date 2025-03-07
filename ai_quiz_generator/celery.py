from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_quiz_generator.settings')

# Initialize Django
import django
django.setup()

# Create a Celery instance
app = Celery('ai_quiz_generator')

# Optional: Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Set timezone settings
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Tbilisi')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')
