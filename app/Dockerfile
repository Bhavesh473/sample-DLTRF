FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Default command
CMD ["python", "app.py"]
