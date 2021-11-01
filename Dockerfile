FROM python:3.9-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get -y install curl

RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN useradd -ms /bin/bash worker

WORKDIR /app
RUN chown -R worker:worker /app

USER worker


RUN pip install --user pipenv

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker Pipfile Pipfile.* /app/

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY --chown=worker:worker . /app

CMD ["pipenv", "run", "celery", "-A", "workers.meta_critic", "worker", "-l", "info"]
