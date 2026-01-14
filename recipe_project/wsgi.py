"""
WSGI config for recipe_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set the default Django settings module for the 'recipe_project' project.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_project.settings')

# Get the WSGI application object
application = get_wsgi_application()

# Wrap the application with WhiteNoise to serve static files efficiently
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'), prefix='static/')
