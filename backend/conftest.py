"""
Django test configuration for pytest
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'syrupstore.settings')
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['DB_NAME'] = ':memory:'

django.setup()
