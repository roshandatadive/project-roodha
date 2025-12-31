import logging
 
# Create a logger for our backend
logger = logging.getLogger("jobwork-backend")
 
# Set log level (INFO = normal production level)
logger.setLevel(logging.INFO)
 
# Format of log messages
# Example:
# 2025-01-01 10:00:00 | INFO | jobwork-backend | message
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
 
# Console handler (prints logs on terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
 
# Avoid duplicate logs
if not logger.handlers:
    logger.addHandler(console_handler)
 