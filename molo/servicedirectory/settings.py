from django.conf import settings

SERVICE_DIRECTORY_API_BASE_URL = getattr(
    settings, 'SERVICE_DIRECTORY_API_BASE_URL', 'http://0.0.0.0:8000/api/'
)

SERVICE_DIRECTORY_API_LOGIN = getattr(
    settings, 'SERVICE_DIRECTORY_API_LOGIN', {
        'username': 'root', 'password': 'adminadmin'
    }
)

GOOGLE_PLACES_API_SERVER_KEY = getattr(
    settings, 'GOOGLE_PLACES_API_SERVER_KEY', 'THIS IS A NONSENSE KEY'
)
