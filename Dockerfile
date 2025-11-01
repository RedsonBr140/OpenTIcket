FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . /app/

# Create persistent directories
RUN mkdir -p /app/logs /app/media /app/static

# Expose Django port
EXPOSE 8000

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && python manage.py compilemessages && gunicorn OpenTIcket.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
