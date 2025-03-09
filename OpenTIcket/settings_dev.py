from .settings import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_PASSWORD_VALIDATORS = []
