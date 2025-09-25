# run.py
import logging
from flask import request
from flask_migrate import Migrate
from application import create_app, db, models

# Configure logger (OTel auto-instrumentation enriches with trace/span IDs)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = create_app()
migrate = Migrate(app, db)


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
    logger.info("Starting Flask application on port 5003...")
    app.run(host="0.0.0.0", port=5003)
