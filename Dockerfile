FROM python:3.10

# Install system dependencies including distutils
RUN apt-get update && apt-get install -y \
    wget curl unzip \
    chromium \
    chromium-driver \
    python3-distutils

# Set environment variables for Chrome & Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your script (replace with your actual script name)
CMD ["python", "main.py"]