# syntax=docker/dockerfile:1

# Use the same Python version as the local dev environment (3.14)
FROM python:3.14-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (layer cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source
COPY . .

# Expose the uvicorn port
EXPOSE 8000

# Run seed.py (idempotent — safe to call on every container start) then
# start the API server. The seed script creates the schema and inserts data
# only if the students table is empty, so repeated `docker compose up` calls
# do not duplicate rows.
CMD ["sh", "-c", "python seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
