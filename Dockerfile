FROM python:3.11-slim-buster

# Set the working directory
WORKDIR /app

# Install Firefox ESR, dependencies, and wget
RUN apt-get update && apt-get install -y firefox-esr wget unzip xvfb libgdk-pixbuf2.0-0 libgtk-3-0 libdbus-glib-1-2 fonts-liberation xdg-utils && rm -rf /var/lib/apt/lists/*

# Download and install geckodriver (adjust version as needed)
ARG GECKODRIVER_VERSION=0.33.0
RUN wget https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin/ && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz

# Copy the repository contents to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure geckodriver is executable
RUN chmod +x /usr/local/bin/geckodriver

# Copy the service account key
COPY gc_user.json /app/gc_user.json

# Set the environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gc_user.json

# Command to run the script
CMD ["python", "scrapper.py"]