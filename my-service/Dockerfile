# Build stage
FROM python:3.12-slim as builder

# Install poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml ./

# Configure poetry to create the virtualenv inside the project directory
RUN poetry config virtualenvs.in-project true

# Install dependencies
RUN poetry install --only main --no-root

# Runtime stage
FROM python:3.12-slim as runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv ./.venv
COPY my_service ./my_service

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 9000

# Command to run the application
CMD ["python", "-m", "my_service.main"]
