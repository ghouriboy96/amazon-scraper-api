FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip \
    chromium \
    chromium-driver

# Set environment variables for Chrome & Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy your app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your script (change this if your script has another name)
CMD ["python", "main.py"]