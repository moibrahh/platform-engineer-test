FROM python:3.12-slim

# Install poetry
RUN pip install poetry

WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.toml ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main --no-interaction --no-root

# Copy application code
COPY my_service/ ./my_service/

# Run the application
CMD ["poetry", "run", "uvicorn", "my_service.main:app", "--host", "0.0.0.0", "--port", "8080"]