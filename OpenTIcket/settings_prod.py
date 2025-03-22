from .settings import *

DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")  # Replace with your SMTP host
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # Your email address
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # Your email password
EMAIL_PORT = env.int("EMAIL_PORT", default=465)  # SMTP port
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=True)  # Use SSL for secure connection
