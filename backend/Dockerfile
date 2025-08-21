# ---- Secure & Minimal Base ----
FROM python:3.10-slim-bullseye

# ---- Set working directory ----
WORKDIR /app

# ---- Install minimal system dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- Copy app source code ----
COPY . .

# ---- Environment configs ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=production

# ---- Expose FastAPI port ----
EXPOSE 8000

# ---- Run FastAPI with Uvicorn ----
# In production, we bind to 0.0.0.0 so Docker can expose it
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]