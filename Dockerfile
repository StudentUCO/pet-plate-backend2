FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "api.py" ]
CMD [ "python", "pub.py" ]
CMD [ "python", "sub.py" ]
