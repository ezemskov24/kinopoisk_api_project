FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /server

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY /server /server

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

