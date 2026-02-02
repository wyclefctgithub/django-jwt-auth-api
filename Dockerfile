# Use Python 3.11 image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["gunicorn", "jwt_auth_api.wsgi:application", "--bind", "0.0.0.0:8000"]
