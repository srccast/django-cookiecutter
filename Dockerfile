FROM python:3.12 as app
RUN pip install docker flask
WORKDIR /app
COPY app.py /app/app.py


FROM python:3.12 as cookiecutter
RUN pip install pipx
RUN pipx install cookiecutter
CMD /root/.local/bin/cookiecutter https://github.com/cookiecutter/cookiecutter-django --config-file /data/config.yaml --no-input
WORKDIR /data