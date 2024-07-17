FROM python:3.12 AS app

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY app.py /app/app.py
COPY templates /app/templates


FROM python:3.12 AS cookiecutter

RUN pip install pipx
RUN pipx install cookiecutter
WORKDIR /data
CMD /root/.local/bin/cookiecutter https://github.com/cookiecutter/cookiecutter-django --config-file /data/config.yaml --no-input


FROM docker as cookiecutter_builder

RUN apk add --no-cache bash

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /bin/wait-for-it
RUN chmod +x /bin/wait-for-it
