import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'train_id'):
            log_entry['train_id'] = record.train_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = True
) -> logging.Logger:
    """Setup logger with console and optional file output"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter() if json_format else formatter)
        logger.addHandler(file_handler)
    
    return logger

# Application loggers
app_logger = setup_logger("train_system.app")
api_logger = setup_logger("train_system.api")
db_logger = setup_logger("train_system.database")
ml_logger = setup_logger("train_system.ml")
optimization_logger = setup_logger("train_system.optimization")
simulation_logger = setup_logger("train_system.simulation")

def get_logger(name: str) -> logging.Logger:
    """Get logger by name"""
    return logging.getLogger(f"train_system.{name}")

class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__.lower())
