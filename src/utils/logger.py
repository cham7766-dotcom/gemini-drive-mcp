"""로깅 유틸리티"""
import logging
from pathlib import Path


def setup_logger(name: str, log_file: Path = None, level: str = "INFO") -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (None이면 파일에 저장하지 않음)
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)

    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 기존 핸들러 제거
    if logger.handlers:
        logger.handlers.clear()

    # 포맷터 생성
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 파일 핸들러 추가 (파일 경로가 제공된 경우)
    if log_file:
        log_dir = log_file.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 콘솔 핸들러는 MCP 서버에서는 사용하지 않음
    # (stdio를 MCP 통신에 사용하므로)

    return logger
