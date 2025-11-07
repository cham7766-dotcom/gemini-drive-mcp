"""OAuth 인증 API"""
from flask import Blueprint, request, jsonify, redirect, current_app
from google_auth_oauthlib.flow import Flow
from pathlib import Path
from src.utils.config import Config
from src.utils.logger import setup_logger

oauth_bp = Blueprint('oauth', __name__)
logger = setup_logger('api.oauth')

# OAuth flow를 저장할 전역 변수
oauth_flow = None


@oauth_bp.route('/oauth/authorize', methods=['GET'])
def authorize():
    """OAuth 인증 시작"""
    global oauth_flow

    try:
        config = Config()
        creds_path = config.get_credentials_path()

        if not creds_path.exists():
            return jsonify({
                'success': False,
                'error': 'credentials.json 파일이 없습니다'
            }), 400

        # OAuth Flow 생성
        oauth_flow = Flow.from_client_secrets_file(
            str(creds_path),
            scopes=['https://www.googleapis.com/auth/drive.file'],
            redirect_uri='http://localhost:5000/api/oauth/callback'
        )

        # 인증 URL 생성
        auth_url, state = oauth_flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        return jsonify({
            'success': True,
            'auth_url': auth_url
        })

    except Exception as e:
        logger.error(f"OAuth 인증 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@oauth_bp.route('/oauth/callback', methods=['GET'])
def callback():
    """OAuth 콜백 처리"""
    global oauth_flow

    try:
        if not oauth_flow:
            return "OAuth flow가 초기화되지 않았습니다. 다시 시도해주세요.", 400

        # 인증 코드로 토큰 교환
        oauth_flow.fetch_token(authorization_response=request.url)

        # 토큰 저장
        credentials = oauth_flow.credentials
        config = Config()
        token_path = config.get_project_root() / 'config' / 'token.json'

        # 토큰을 JSON 파일로 저장
        import json
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        with open(token_path, 'w') as f:
            json.dump(token_data, f)

        logger.info("OAuth 토큰 저장 완료")

        # Drive 클라이언트 재초기화
        from src.clients.drive_client import DriveClient
        creds_path = config.get_credentials_path()
        current_app.config['DRIVE_CLIENT'] = DriveClient(str(creds_path))
        logger.info("Drive 클라이언트 재초기화 성공")

        # 성공 페이지 반환
        return """
        <html>
        <head>
            <title>인증 완료</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .message {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                h1 { color: #4caf50; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>✅ 인증 완료!</h1>
                <p>Google Drive 연결이 완료되었습니다.</p>
                <p>이 창을 닫아주세요.</p>
            </div>
            <script>
                setTimeout(() => window.close(), 2000);
            </script>
        </body>
        </html>
        """

    except Exception as e:
        logger.error(f"OAuth 콜백 처리 실패: {e}")
        return f"""
        <html>
        <head>
            <title>인증 실패</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .message {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                h1 {{ color: #f44336; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="message">
                <h1>❌ 인증 실패</h1>
                <p>오류: {str(e)}</p>
                <p>다시 시도해주세요.</p>
            </div>
        </body>
        </html>
        """, 500


@oauth_bp.route('/oauth/status', methods=['GET'])
def status():
    """OAuth 인증 상태 확인"""
    try:
        config = Config()
        token_path = config.get_project_root() / 'config' / 'token.json'
        drive_client = current_app.config.get('DRIVE_CLIENT')

        return jsonify({
            'authenticated': token_path.exists() and drive_client is not None
        })

    except Exception as e:
        logger.error(f"OAuth 상태 확인 실패: {e}")
        return jsonify({
            'authenticated': False
        })
