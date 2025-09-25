# run.py
import logging
from flask import request, g
from flask.sessions import SecureCookieSessionInterface
from flask_login import user_loaded_from_header
from flask_migrate import Migrate

from application import create_app, db, models

# Configure logging (trace_id and span_id will be auto-injected by OTel)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = create_app()
migrate = Migrate(app, db)


class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""

    def save_session(self, *args, **kwargs):
        if g.get("login_via_header"):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)


app.session_interface = CustomSessionInterface()


@user_loaded_from_header.connect
def user_loaded_from_header(self, user=None):
    g.login_via_header = True


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
    logger.info("Starting Flask application on port 5001...")
    app.run(host="0.0.0.0", port=5001)
