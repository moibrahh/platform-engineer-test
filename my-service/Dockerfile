FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.toml ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction

# Copy application code
COPY my_service/ ./my_service/

# Expose port
EXPOSE 9000

# Run the application
CMD ["poetry", "run", "python", "-m", "my_service.main"]