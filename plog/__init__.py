import sys

from loguru import logger


log_path = "/var/log/healthcheck.log"
error_path = "/var/log/error_healthcheck.log"
try:
    logger.configure(
        handlers=[
            dict(sink=sys.stderr),
            dict(sink=log_path, enqueue=False, rotation=1e+7),  # approx. 10Mb for rotating files
            dict(sink=error_path, enqueue=False, rotation=1e+7, level="error"),
        ],
    )
except PermissionError:
    logger.configure(handlers=[dict(sink=sys.stderr)])
