from loguru import logger

logger.add("logs/api.log", rotation="1 MB", level="DEBUG")
