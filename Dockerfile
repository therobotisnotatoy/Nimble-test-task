FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y cron

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV $(cat .env | xargs)

EXPOSE 8000

RUN touch /app/logs/cron_job.log
RUN chmod +x /app/cron_job && crontab /app/cron_job

RUN python -m unittest tests/test_app_config.py tests/test_db_manager.py
RUN python -m unittest tests/test_utils.py tests/test_cron_job.py

CMD cron && uvicorn app:app --host 0.0.0.0 --port 8000
