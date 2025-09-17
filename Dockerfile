FROM python:3.11-slim

# Install system dependencies for Node.js, Java, and g++
RUN apt-get update && apt-get install -y \
    curl \
    default-jdk \
    g++ \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY api/ .

# Expose default port
EXPOSE 5000

# Run with gunicorn
CMD sh -c "gunicorn -w 4 -b 0.0.0.0:$PORT server:app"
