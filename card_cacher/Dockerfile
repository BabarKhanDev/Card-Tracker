FROM python:3.12

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg

COPY ./requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt
COPY . .

EXPOSE 5001
CMD ["flask", "run", "-p", "5001", "--host", "0.0.0.0"]