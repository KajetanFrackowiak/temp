FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxi6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    libgconf-2-4 \
    libgl1-mesa-glx \
    ca-certificates \
    fonts-liberation \
    cron \
    libxss1 \
    libappindicator3-1 \
    --fix-missing \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y

# Install ChromeDriver (latest version)
RUN CHROME_DRIVER_VERSION=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/

# Copy the cron job into the container
COPY cronjob /etc/cron.d/tiktok-cron

# Set permissions for the cron job file
RUN chmod 0644 /etc/cron.d/tiktok-cron

# Apply the cron job
RUN crontab /etc/cron.d/tiktok-cron

# Create the cron.log file and set permissions
RUN touch /var/log/cron.log && chmod 666 /var/log/cron.log

# Set environment variables for Chrome to run in headless mode
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (if necessary, for web apps)
EXPOSE 8080

# Start cron and run the Python script
CMD cron && tail -f /var/log/cron.log
