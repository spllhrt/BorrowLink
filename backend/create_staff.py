import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User

username = "admin"
password = "qwerty"
email = "admin@gmail.com"

if not User.objects.filter(username=username).exists():
    staff_user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    staff_user.is_staff = True
    staff_user.save()
    print("✅ Staff user created:", username)
else:
    print("⚠️ User already exists")
