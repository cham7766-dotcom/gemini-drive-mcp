"""Google Drive API"""
import asyncio
from flask import Blueprint, request, jsonify, current_app
from src.utils.logger import setup_logger

drive_bp = Blueprint('drive', __name__)
logger = setup_logger('api.drive')


def get_drive_client():
    return current_app.config.get('DRIVE_CLIENT')


@drive_bp.route('/save', methods=['POST'])
def save_to_drive():
    """
    Drive에 코드 저장 API

    Request:
    {
        "code": "def fibonacci(n): ...",
        "filename": "fibonacci.py",
        "folder": "GeminiCodeGeneration"  // 선택사항
    }

    Response:
    {
        "success": true,
        "file_id": "1abc...",
        "web_view_link": "https://drive.google.com/..."
    }
    """
    try:
        drive_client = get_drive_client()
        from src.utils.config import Config

        data = request.get_json()
        if not data or 'code' not in data or 'filename' not in data:
            return jsonify({
                'success': False,
                'error': 'code와 filename 필드가 필요합니다'
            }), 400

        code = data['code']
        filename = data['filename']
        folder_name = data.get('folder', Config.get_drive_folder_name())

        if not drive_client:
            return jsonify({
                'success': False,
                'error': 'Drive 클라이언트가 초기화되지 않았습니다'
            }), 500

        # 폴더 생성 또는 찾기
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            folder_id = loop.run_until_complete(
                drive_client.create_folder(folder_name)
            )

            # 파일 업로드
            result = loop.run_until_complete(
                drive_client.upload_file(
                    content=code,
                    filename=filename,
                    folder_id=folder_id
                )
            )
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'file_id': result['file_id'],
            'file_name': result['file_name'],
            'web_view_link': result['web_view_link']
        })

    except Exception as e:
        logger.error(f"파일 저장 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
