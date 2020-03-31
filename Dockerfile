FROM python:3-alpine

RUN mkdir -p /app/src

COPY src /app/src

WORKDIR /app

ENV PORT 80

ENV PYTHONPATH /app

ENTRYPOINT ["python", "src/main.py"]

EXPOSE 80
