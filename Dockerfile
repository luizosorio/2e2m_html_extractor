FROM python:3.10

ENV CHROME_VERSION=google-chrome-stable
ENV DISPLAY=:99
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    wget \
    gnupg \
    ca-certificates \
    libxss1 \
    libnss3 \
    libasound2 \
    libappindicator3-1 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends $CHROME_VERSION && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install && playwright install-deps

COPY 2e2m .

RUN chmod +x /app/the_x.sh
CMD ["bash", "-c", "/app/the_x.sh && uvicorn html_extractor:app --host 0.0.0.0 --port 8000"]
