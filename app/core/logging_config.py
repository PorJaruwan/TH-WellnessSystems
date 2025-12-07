# app/core/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os
from pythonjsonlogger import jsonlogger

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 🔸 กำหนดระดับ log per module
MODULE_LOG_LEVELS = {
    "service.company": "INFO",
    #"service.patient": "DEBUG",
    #"service.booking": "INFO",
    #"service.payment": "WARNING",
}

# 🔸 เก็บ logger ที่สร้างแล้ว
LOGGERS = {}

def get_service_logger(name: str) -> logging.Logger:
    if name in LOGGERS:
        return LOGGERS[name]

    logger = logging.getLogger(name)
    log_level = MODULE_LOG_LEVELS.get(name, "INFO")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # ป้องกันการเพิ่ม handler ซ้ำ
    if not logger.handlers:
        # 🔹 Formatter
        json_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        std_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        # 🔸 Console handler (ใช้ formatter ปกติ)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(std_formatter)

        # 🔸 File handler แยก per module
        module_log_file = os.path.join(LOG_DIR, f"{name}.log")
        module_file_handler = RotatingFileHandler(module_log_file, maxBytes=2_000_000, backupCount=2)
        module_file_handler.setFormatter(json_formatter)

        # 🔸 Shared file handler สำหรับรวม log ทั้งหมด
        shared_log_file = os.path.join(LOG_DIR, "app.log")
        shared_file_handler = RotatingFileHandler(shared_log_file, maxBytes=5_000_000, backupCount=5)
        shared_file_handler.setFormatter(json_formatter)

        # ✅ Add all handlers
        logger.addHandler(console_handler)
        logger.addHandler(module_file_handler)
        logger.addHandler(shared_file_handler)

    LOGGERS[name] = logger
    return logger
