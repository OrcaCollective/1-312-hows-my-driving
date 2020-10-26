FROM python:3.9-slim

ENV PYTHONUNBUFFERED=true

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY src/ /app

CMD ["flask", "run", "--host=0.0.0.0"]


