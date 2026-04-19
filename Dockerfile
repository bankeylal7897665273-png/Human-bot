# Python 3.10 ka lightweight version
FROM python:3.10-slim

WORKDIR /app

# Requirements install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki files copy karna
COPY . .

# Render ke liye port expose karna
EXPOSE 10000

# Gunicorn ke through app run karna (Best for Render)
CMD ["gunicorn", "bot:app", "--bind", "0.0.0.0:10000"]
