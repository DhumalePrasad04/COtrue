
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y gcc && \
    pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
