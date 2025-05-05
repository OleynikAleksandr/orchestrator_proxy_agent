FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 8001 21001 8002

# Run all components
CMD ["bash", "-c", \
     "python -m fastchat.serve.controller --host 0.0.0.0 --port 21001 & \
      python -m orcestator.proxy_worker --model-id orcestator \
             --controller http://localhost:21001 --port 8002 & \
      python -m orcestator.api_server --host 0.0.0.0 --port 8000"]
