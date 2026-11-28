FROM python:3.11.9

WORKDIR /main

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .