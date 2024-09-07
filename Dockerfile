FROM python:3.11-slim-bookworm as base

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl git build-essential \
    && apt-get autoremove -y \
    && apt-get install -y awscli \
    && apt-get install -y postgresql-client \  
    && apt-get install -y less

FROM base AS install

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app /app/app
COPY ./logging_config.ini /app/logging_config.ini
RUN touch ./debug.log
RUN touch ./error.log
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]