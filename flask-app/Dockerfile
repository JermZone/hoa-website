FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-login flask-sqlalchemy flask-wtf

# Expose port
EXPOSE 5000

# Start the app
CMD ["python", "run.py"]
