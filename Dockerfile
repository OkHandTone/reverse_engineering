FROM python:3.10.13-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y libpq-dev \
  && apt-get install -y gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

RUN python -m venv $VIRTUAL_ENV \
  && pip install -r /requirements.txt --no-cache-dir

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
