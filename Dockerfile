# Use slim Python image
FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Install dependencies for wkhtmltopdf and general tools
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from Debian repo (stable)
RUN apt-get update && apt-get install -y wkhtmltopdf && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies file
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Command to run your Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
