"""유틸리티 함수 모듈"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Colorama 초기화
init(autoreset=True)

def setup_logging(log_file="logs/app.log", level=logging.INFO):
    """로깅 시스템 설정"""
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("GeminiDriveMCP")
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_config():
    """환경 변수 로드"""
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    env_path = project_root / "config" / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
    
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LOG_FILE": os.getenv("LOG_FILE", "logs/app.log"),
        "DRIVE_FOLDER_NAME": os.getenv("DRIVE_FOLDER_NAME", "GeminiCodeGeneration"),
    }

def get_project_root():
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent

def ensure_dir(directory):
    """디렉토리 생성"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def print_success(message):
    """성공 메시지 출력"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """에러 메시지 출력"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """정보 메시지 출력"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    """경고 메시지 출력"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
