FROM python:3.8-slim

RUN pip install kubernetes

COPY api-tester.py /app.py

ENTRYPOINT ["python", "/app.py"]
