FROM python:3.9-alpine

WORKDIR /opt/app

# Copy over the requirements file first to cache the installed dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && adduser -D -H petal -u 1001

# Copy the app.py
COPY app.py app.py

# DROP ROOT PRIVILEGES
USER 1001

# Gunicorn to start the app with 4 workers
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
