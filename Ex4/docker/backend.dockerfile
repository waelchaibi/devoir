FROM python:3.11-slim

WORKDIR /app

COPY backend/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src/app.py .

CMD ["python", "app.py"]
