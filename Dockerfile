FROM python:3.9-alpine

WORKDIR /opt/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && adduser -D -H petal -u 1001
COPY . .

  # DROP ROOT PRIVLEGES
USER 1001
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
