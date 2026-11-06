FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=9580

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates
COPY static ./static
COPY samples.txt .

RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 9580
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:9580", "--timeout", "120", "app:app"]
