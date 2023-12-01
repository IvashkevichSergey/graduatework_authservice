FROM python:3.11

WORKDIR ./app

COPY ./pyproject.toml .

RUN pip3 install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

COPY . .

