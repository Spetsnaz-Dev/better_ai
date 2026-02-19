import logging
import os
import sys
import time
from flask import request, g, current_app
from .utils.formatters import JSONFormatter


def init_app_logging(app):
    """Configure global logger and install request/response middleware.

    This replaces the former standalone ``setup_logging`` approach.  The
    function is invoked with the Flask application instance so that every
    incoming request and outgoing response is logged in a structured JSON
    format.  The logger itself is configured exactly as before, but it is
    now tied to Flask's lifecycle via ``before_request``/``after_request``
    handlers.
    """

    # base logger configuration (mimics old setup_logging behavior)
    log_level = os.getenv("LOG_LEVEL", "INFO")

    root = logging.getLogger()
    if root.handlers:
        for handler in list(root.handlers):
            root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root.setLevel(log_level)
    root.addHandler(handler)

    # request logging middleware
    @app.before_request
    def _start_timer():
        g.start_time = time.time()
        current_app.logger.info("Incoming request",
                                extra={"metadata": {"method": request.method,
                                                       "path": request.path}})

    @app.after_request
    def _log_response(response):
        duration = time.time() - g.get("start_time", time.time())
        current_app.logger.info("Request completed",
                                extra={"metadata": {"method": request.method,
                                                       "path": request.path,
                                                       "status": response.status_code,
                                                       "duration": duration}})
        return response
