FROM python:3.12-slim

WORKDIR /app

# Install dependencies dulu (layer terpisah agar cache efisien)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua source code
COPY app.py database.py schema.sql ./

# Railway akan mount volume ke /data — kita set lewat env var
ENV DB_DIR=/data

# Streamlit perlu config ini agar bisa jalan tanpa browser
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLE_CORS=false

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
