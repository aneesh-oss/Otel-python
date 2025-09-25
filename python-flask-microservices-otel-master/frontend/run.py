# run.py
import logging
from application import create_app
from flask import request

# Configure logging (OTel auto-instrumentation will inject trace/span IDs)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = create_app()

@app.before_request
def log_request():
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
        },
    )

@app.after_request
def log_response(response):
    logger.info(
        "Outgoing response",
        extra={
            "status_code": response.status_code,
            "path": request.path,
        },
    )
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception occurred", extra={"path": request.path})
    return {"error": str(e)}, 500

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(host="0.0.0.0", port=5000)
