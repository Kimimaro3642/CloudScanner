FROM python:3.12-slim
WORKDIR /app
COPY scanner/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY scanner/src /app/scanner/src
ENTRYPOINT ["python","/app/scanner/src/main.py"]
