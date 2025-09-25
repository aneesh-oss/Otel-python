# Dockerfile
FROM python:3.7
COPY requirements.txt /productapp/requirements.txt
WORKDIR /productapp
RUN pip install -r requirements.txt
RUN pip install \
    opentelemetry-distro \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation \
    opentelemetry-instrumentation-logging \
    opentelemetry-instrumentation-requests \
    opentelemetry-instrumentation-flask
COPY . /productapp
ENTRYPOINT ["opentelemetry-instrument"]
CMD ["python","run.py"]