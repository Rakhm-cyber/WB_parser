FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["python", "bot.py"]
