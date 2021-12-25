import os

from django.core.wsgi import get_wsgi_application

from accounts.models import CustomUser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

admin_username = os.environ.get('DJANGO_ADMIN_USERNAME')
admin_queryset = CustomUser.objects.filter(username=admin_username)
if admin_queryset.count() is 0:
    CustomUser.objects.create_superuser(username=admin_username,
                                        email=os.environ.get('DJANGO_ADMIN_EMAIL'),
                                        password=os.environ.get('DJANGO_ADMIN_PASSWORD'),
                                        is_active=True, is_staff=True)
