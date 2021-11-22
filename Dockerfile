FROM python:3.9-slim-buster

ENV PROJECT_ROOT="/opt/aiohttp-milvus/"
ENV PYTHONPATH=${PYTHONPATH}:${PROJECT_ROOT}

WORKDIR ${PROJECT_ROOT}


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install

RUN apt-get autoremove -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

ADD . ./

EXPOSE 8080

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "src.main:app"]