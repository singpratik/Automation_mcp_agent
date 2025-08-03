# Use stable Python
FROM python:3.11-slim

# Install system dependencies for playwright + browser-use
RUN apt-get update && apt-get install -y \
    curl unzip wget xvfb libnss3 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpangocairo-1.0-0 fonts-liberation libappindicator3-1 libxshmfence1 lsb-release \
    && apt-get clean

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright dependencies
RUN playwright install --with-deps

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app directly
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
