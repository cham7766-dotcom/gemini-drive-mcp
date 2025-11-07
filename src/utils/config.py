"""환경 설정 관리"""
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """환경 설정 클래스"""

    _instance = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not Config._loaded:
            self._load_env()
            Config._loaded = True

    def _load_env(self):
        """환경 변수 로드"""
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        env_path = project_root / "config" / ".env"

        if env_path.exists():
            load_dotenv(env_path)

    @staticmethod
    def get_project_root() -> Path:
        """프로젝트 루트 디렉토리 반환"""
        return Path(__file__).parent.parent.parent

    @staticmethod
    def get_gemini_api_key() -> str:
        """Gemini API 키 반환"""
        return os.getenv("GEMINI_API_KEY", "")

    @staticmethod
    def get_credentials_path() -> Path:
        """Google OAuth 인증 파일 경로"""
        return Config.get_project_root() / "config" / "credentials.json"

    @staticmethod
    def get_token_path() -> Path:
        """Google OAuth 토큰 파일 경로"""
        return Config.get_project_root() / "config" / "token.json"

    @staticmethod
    def get_drive_folder_name() -> str:
        """기본 Drive 폴더 이름"""
        return os.getenv("DRIVE_FOLDER_NAME", "GeminiCodeGeneration")

    @staticmethod
    def get_log_level() -> str:
        """로그 레벨 반환"""
        return os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def get_log_file() -> Path:
        """로그 파일 경로 반환"""
        log_file = os.getenv("LOG_FILE", "logs/mcp_server.log")
        return Config.get_project_root() / log_file

    @staticmethod
    def ensure_dir(directory: Path):
        """디렉토리 생성"""
        directory.mkdir(parents=True, exist_ok=True)
