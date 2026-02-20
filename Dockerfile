FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install poetry && poetry install --no-root
COPY . .
CMD ["poetry", "run", "python", "server.py"]
