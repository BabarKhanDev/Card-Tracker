FROM python:3.11

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt
COPY . .

EXPOSE 8080
CMD ["flask", "run", "-p", "8080", "--host", "0.0.0.0"]