import logging
logger = logging.getLogger("doc_generator")

logger.setLevel(logging.INFO)

# Terminal handler
console_handler = logging.StreamHandler()

# File handler
file_handler = logging.FileHandler("app.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)