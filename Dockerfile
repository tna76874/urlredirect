FROM python:3.9

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git libgl1 libmagic1

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt && chmod -R +x /app

COPY main.py /app/main.py
COPY helper.py /app/helper.py
COPY redirectmanager /app/redirectmanager
COPY urldb.py /app/urldb.py
COPY version.py /app/version.py
COPY version_cli.py /app/version_cli.py
RUN chmod -R +x /app

COPY .git /app/.git
RUN git --git-dir=/app/.git rev-parse HEAD > COMMIT_HASH && \
    python version_cli.py . ./redirectmanager && \
    rm -rf /app/.git

EXPOSE 5000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["sh", "-c", "/app/entrypoint.sh"]
