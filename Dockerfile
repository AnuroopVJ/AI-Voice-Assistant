FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure db folders exist
RUN mkdir -p /workspaces/Kyle_AI_Voice_Assistant_RT/dbs/vector \
    && mkdir -p /workspaces/Kyle_AI_Voice_Assistant_RT/dbs/history

CMD ["python", "agents.py"]
