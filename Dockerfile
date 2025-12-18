FROM python:3.12-slim

RUN useradd --create-home --uid 10001 placer
WORKDIR /app
COPY main.py solver.py helpers.py input.txt ./
USER placer

ENTRYPOINT ["python", "main.py"]
