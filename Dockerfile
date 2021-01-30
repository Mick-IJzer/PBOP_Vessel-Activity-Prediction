FROM python:3.9

WORKDIR /app
EXPOSE 2021

COPY ./Dashboard/requirements.txt .
RUN pip install -r requirements.txt

COPY ./Dashboard .

CMD ["python","main.py"]



