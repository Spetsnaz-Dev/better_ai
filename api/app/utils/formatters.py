"""
Reusable logging formatters.
"""
import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter.
    
    Format: timestamp | level | module | message | metadata
    """
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
            "metadata": getattr(record, "metadata", {})
        }
        return json.dumps(log_entry)
