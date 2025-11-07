"""파일 관리 API"""
import asyncio
from flask import Blueprint, request, jsonify, current_app
from src.utils.logger import setup_logger

files_bp = Blueprint('files', __name__)
logger = setup_logger('api.files')


def get_drive_client():
    return current_app.config.get('DRIVE_CLIENT')


@files_bp.route('/files', methods=['GET'])
def list_files():
    """
    Drive 파일 목록 조회 API

    Query Parameters:
    - folder: 폴더명 (기본값: GeminiCodeGeneration)

    Response:
    {
        "success": true,
        "files": [
            {
                "id": "1abc...",
                "name": "fibonacci.py",
                "created_at": "2025-11-07T14:38:57",
                "web_view_link": "https://..."
            }
        ]
    }
    """
    try:
        drive_client = get_drive_client()
        from src.utils.config import Config

        folder_name = request.args.get('folder', Config.get_drive_folder_name())

        if not drive_client:
            return jsonify({
                'success': False,
                'error': 'Drive 클라이언트가 초기화되지 않았습니다'
            }), 500

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 폴더 찾기
            folder_id = loop.run_until_complete(
                drive_client.create_folder(folder_name)
            )

            # 파일 목록 조회
            files = loop.run_until_complete(
                drive_client.list_files(folder_id=folder_id)
            )
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'files': files
        })

    except Exception as e:
        logger.error(f"파일 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@files_bp.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    """
    Drive 파일 읽기 API

    Response:
    {
        "success": true,
        "filename": "fibonacci.py",
        "content": "def fibonacci(n): ...",
        "language": "python"
    }
    """
    try:
        drive_client = get_drive_client()

        if not drive_client:
            return jsonify({
                'success': False,
                'error': 'Drive 클라이언트가 초기화되지 않았습니다'
            }), 500

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                drive_client.download_file(file_id)
            )
        finally:
            loop.close()

        # 파일 확장자로 언어 추정
        filename = result['file_name']
        language = _detect_language_from_filename(filename)

        return jsonify({
            'success': True,
            'filename': filename,
            'content': result['content'],
            'language': language
        })

    except Exception as e:
        logger.error(f"파일 읽기 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _detect_language_from_filename(filename: str) -> str:
    """파일명에서 언어 감지"""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.sh': 'bash',
    }

    for ext, lang in ext_map.items():
        if filename.endswith(ext):
            return lang

    return 'text'
