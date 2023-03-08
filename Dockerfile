FROM python:3-alpine

COPY . /app
WORKDIR /app

RUN python3 -m pip config --user set global.index-url https://pypi.org/simple \
    && python3 -m pip config --user set global.timeout 150 \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --only main

ENTRYPOINT [ "python3"]
CMD [ "/app/app.py"]