FROM python:3.11-slim
WORKDIR /app
COPY requirements-common.txt /tmp/requirements-common.txt
RUN pip install --no-cache-dir -r /tmp/requirements-common.txt
COPY services/common/metrics.py /app/metrics.py
COPY services/product-service/main.py /app/main.py
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
