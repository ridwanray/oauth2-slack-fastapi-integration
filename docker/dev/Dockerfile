# Pull official base image 
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN pip install poetry==1.3.0
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . .
