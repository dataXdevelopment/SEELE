FROM python:3.9-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get -y install curl

RUN useradd -ms /bin/bash worker

WORKDIR /app
RUN chown -R worker:worker /app

USER worker

RUN pip install --user pipenv

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker Pipfile Pipfile.* /app/

RUN pipenv install --deploy --system

COPY --chown=worker:worker . /app

CMD [ "python", "workers/test_worker.py" ]
