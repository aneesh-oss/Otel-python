# Dockerfile
FROM python:3.7
COPY requirements.txt /frontendapp/requirements.txt
WORKDIR /frontendapp
RUN pip install -r requirements.txt
# RUN pip install \
#     opentelemetry-distro \
#     opentelemetry-exporter-otlp \
#     opentelemetry-instrumentation \
#     opentelemetry-instrumentation-logging \
#     opentelemetry-instrumentation-requests \
#     opentelemetry-instrumentation-flask
COPY . /frontendapp
ENTRYPOINT ["opentelemetry-instrument"]
CMD ["python","run.py"]