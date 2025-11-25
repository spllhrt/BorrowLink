import os
import sys

# Add the Django project directory to the Python path
path = '/home/hayett/BorrowLink/backend'
if path not in sys.path:
    sys.path.append(path)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
