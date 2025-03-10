FROM python:3.12
WORKDIR /app
COPY app.py .
COPY tools.py .
COPY config.json .
COPY requirements.txt .
RUN pip install -r requirements.txt
