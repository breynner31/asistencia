FROM python:3.10-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5003

CMD ["python", "bot.py"]
