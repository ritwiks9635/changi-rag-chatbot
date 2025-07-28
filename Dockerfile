# ---- Secure & Minimal Base ----
FROM python:3.10-slim-bullseye

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies (minimal, no recommended extras) ----
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy app source ----
COPY app ./app
COPY main.py .

# ---- Environment configs ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ---- Expose FastAPI port ----
EXPOSE 8000

# ---- Start the app ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
