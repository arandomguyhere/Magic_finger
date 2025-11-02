FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY webscraper/ ./webscraper/
COPY data/ ./data/

# Set the working directory to webscraper for module execution
WORKDIR /app/webscraper

# Default command (can be overridden)
CMD ["python", "-m", "webscraper", "--help"]
