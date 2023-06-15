FROM python:3.11-alpine

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "python api.py & python pub.py & python sub.py" ]
