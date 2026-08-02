# Base python image
FROM python:3.10-slim

# Working directory set करें
WORKDIR /app

# System level packages (अगर SQLite या C extensions चाहिए)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependencies copy और install करें
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application source code copy करें
COPY . .

# Expose API port (serve.py का port, e.g., 8000 या 5000)
EXPOSE 8000

# Default Command application start करने के लिए
CMD ["python", "src/serve.py"]