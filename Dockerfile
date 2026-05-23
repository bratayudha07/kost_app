FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py database.py schema.sql ./

ENV DB_DIR=/data
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Pakai shell form CMD agar $PORT bisa dibaca saat runtime
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
