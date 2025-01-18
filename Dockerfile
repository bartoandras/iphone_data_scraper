# Dockerfile for iPhone Scraper Application
# Sets up the Python environment with Chrome for Selenium and configures cron scheduling

# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium and cron
RUN apt-get update && apt-get install -y wget gnupg cron unzip curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable=132.0.6834.83-1 \
    && rm -rf /var/lib/apt/lists/*

# Install network tools
RUN apt-get update && apt-get install -y \
    dnsutils \
    iputils-ping \
    curl \
    ca-certificates \
    net-tools

# Install matching ChromeDriver version with enhanced error handling
RUN echo "Starting ChromeDriver installation..." && \
    CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_132) && \
    echo "Resolving chromedriver.storage.googleapis.com..." && \
    nslookup chromedriver.storage.googleapis.com && \
    echo "Testing connection to Google Storage..." && \
    curl -I https://chromedriver.storage.googleapis.com && \
    echo "Downloading ChromeDriver version $CHROMEDRIVER_VERSION..." && \
    for i in {1..5}; do \
        echo "Attempt $i/5" && \
        wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
        if [ $? -eq 0 ]; then break; else sleep 5; fi; \
    done && \
    if [ ! -f /tmp/chromedriver.zip ]; then \
        echo "Failed to download ChromeDriver after 5 attempts"; \
        exit 1; \
    fi && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    echo "ChromeDriver installation completed successfully"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cron job
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create logs directory
RUN mkdir -p /var/log/cron

CMD ["/entrypoint.sh"]
