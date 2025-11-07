"""Flask 웹 애플리케이션 메인"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.clients.gemini_client import GeminiClient
from src.clients.drive_client import DriveClient
from src.managers.context_manager import ContextManager
from src.utils.config import Config
from src.utils.logger import setup_logger

# Flask 앱 생성
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

# 로거 설정
logger = setup_logger('web_app',
                     Config.get_project_root() / 'logs' / 'web_app.log',
                     'INFO')

# 전역 클라이언트 인스턴스를 app.config에 저장
def get_gemini_client():
    return app.config.get('GEMINI_CLIENT')

def get_drive_client():
    return app.config.get('DRIVE_CLIENT')

def get_context_manager():
    return app.config.get('CONTEXT_MANAGER')


def init_clients():
    """클라이언트 초기화"""
    try:
        config = Config()

        # Gemini 클라이언트
        api_key = config.get_gemini_api_key()
        if api_key:
            app.config['GEMINI_CLIENT'] = GeminiClient(api_key)
            logger.info("Gemini 클라이언트 초기화 성공")
        else:
            app.config['GEMINI_CLIENT'] = None
            logger.warning("Gemini API 키가 없습니다")

        # Context Manager
        app.config['CONTEXT_MANAGER'] = ContextManager()
        logger.info("Context Manager 초기화 성공")

        return True

    except Exception as e:
        logger.error(f"클라이언트 초기화 실패: {e}")
        return False


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """헬스 체크 엔드포인트"""
    gemini_client = get_gemini_client()
    context_manager = get_context_manager()

    return jsonify({
        'status': 'ok',
        'gemini_ready': gemini_client is not None,
        'context_ready': context_manager is not None
    })


# API 라우트 등록
from src.web.api.generate import generate_bp

app.register_blueprint(generate_bp, url_prefix='/api')


if __name__ == '__main__':
    print("=" * 60)
    print("Gemini-Drive 웹 애플리케이션")
    print("=" * 60)

    # 클라이언트 초기화
    if init_clients():
        print("✓ 클라이언트 초기화 성공")
    else:
        print("⚠️ 일부 클라이언트 초기화 실패 (로그 확인)")

    print("\n웹 서버 시작...")
    print("접속 주소: http://localhost:5000")
    print("Ctrl+C를 눌러 종료하세요\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
