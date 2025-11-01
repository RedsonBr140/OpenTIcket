from .settings import *

DEBUG = True
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static")
]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_PASSWORD_VALIDATORS = []
