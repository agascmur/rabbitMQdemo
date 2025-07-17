FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y nano
#CMD ["python", "scraper.py"]
CMD ["tail", "-f", "/dev/null"]