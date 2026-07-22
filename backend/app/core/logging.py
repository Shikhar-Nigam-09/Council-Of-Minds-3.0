import logging
import json
from datetime import datetime
from app.core.config import settings
from app.core.correlation import CorrelationIdFilter

class RedactFilter(logging.Filter):
    def filter(self, record):
        return True

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        
        if hasattr(record, "request_id") and record.request_id:
            log_record["request_id"] = record.request_id
            
        msg = log_record["message"]
        if "Bearer " in msg or "Authorization" in msg:
            log_record["message"] = "[REDACTED TOKEN]"
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.addFilter(CorrelationIdFilter())
    handler.addFilter(RedactFilter())
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger
