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
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy app source code ----
COPY . .

# ---- Environment configs ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


# ---- Expose default Gradio port ----
# ---- Expose FastAPI port ----
EXPOSE 7860

# ---- Run Gradio app ----
CMD ["python", "-B", "gradio_app.py"]
