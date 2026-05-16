FROM python:3.11-slim
WORKDIR /app
COPY requirements-common.txt /tmp/requirements-common.txt
RUN pip install --no-cache-dir -r /tmp/requirements-common.txt
COPY services/alert-webhook/main.py /app/main.py
EXPOSE 5001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
