"""
WSGI config for FaviconGen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys

# Add the project root directory to the Python path
# This allows 'FaviconGen.settings' to be imported correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaviconGen.settings')

application = get_wsgi_application()

app = application
