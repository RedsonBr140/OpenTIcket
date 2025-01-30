FROM python:3.13-slim AS builder


# Install dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production

FROM python:3.13-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "OpenTIcket.wsgi:application"]