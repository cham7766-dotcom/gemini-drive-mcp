"""코드 생성 API"""
import asyncio
from flask import Blueprint, request, jsonify, current_app
from src.utils.logger import setup_logger

generate_bp = Blueprint('generate', __name__)
logger = setup_logger('api.generate')


def get_gemini_client():
    return current_app.config.get('GEMINI_CLIENT')

def get_context_manager():
    return current_app.config.get('CONTEXT_MANAGER')


@generate_bp.route('/generate', methods=['POST'])
def generate_code():
    """
    코드 생성 API

    Request:
    {
        "prompt": "Python으로 피보나치 수열 만들어줘",
        "language": "python",  // 선택사항
        "context_id": "session_id"  // 선택사항
    }

    Response:
    {
        "success": true,
        "code": "def fibonacci(n): ...",
        "language": "python",
        "explanation": "이 코드는...",
        "session_id": "20251107_143857"
    }
    """
    try:
        gemini_client = get_gemini_client()
        context_manager = get_context_manager()

        # 요청 데이터 확인
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'prompt 필드가 필요합니다'
            }), 400

        prompt = data['prompt']
        language = data.get('language')
        context_id = data.get('context_id')

        # Gemini 클라이언트 확인
        if not gemini_client:
            return jsonify({
                'success': False,
                'error': 'Gemini 클라이언트가 초기화되지 않았습니다'
            }), 500

        # 컨텍스트 로드 (선택사항)
        context = None
        if context_id and context_manager:
            try:
                context_manager.load_session(context_id)
                context = context_manager.get_context()
            except Exception as e:
                logger.warning(f"컨텍스트 로드 실패: {e}")

        # 한글 최적화 프롬프트 구성
        optimized_prompt = _build_korean_prompt(prompt, language)

        # 코드 생성 (async 함수를 동기로 실행)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                gemini_client.generate_code(
                    prompt=optimized_prompt,
                    language=language,
                    context=context
                )
            )
        finally:
            loop.close()

        # 컨텍스트 저장
        if context_manager:
            context_manager.add_interaction(
                user_message=prompt,
                assistant_response=result['code']
            )
            session_id = context_manager.session_id
        else:
            session_id = None

        return jsonify({
            'success': True,
            'code': result['code'],
            'language': result['language'],
            'explanation': result.get('explanation', ''),
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"코드 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@generate_bp.route('/modify', methods=['POST'])
def modify_code():
    """
    코드 수정 요청 API

    Request:
    {
        "original_code": "def fibonacci(n): ...",
        "modification": "재귀 대신 반복문으로 바꿔줘"
    }

    Response:
    {
        "success": true,
        "modified_code": "def fibonacci(n): ...",
        "explanation": "반복문으로 변경했습니다..."
    }
    """
    try:
        gemini_client = get_gemini_client()

        data = request.get_json()
        if not data or 'original_code' not in data or 'modification' not in data:
            return jsonify({
                'success': False,
                'error': 'original_code와 modification 필드가 필요합니다'
            }), 400

        original_code = data['original_code']
        modification = data['modification']

        if not gemini_client:
            return jsonify({
                'success': False,
                'error': 'Gemini 클라이언트가 초기화되지 않았습니다'
            }), 500

        # 수정 요청 프롬프트 구성
        prompt = _build_modification_prompt(original_code, modification)

        # 코드 생성
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                gemini_client.generate_code(prompt=prompt)
            )
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'modified_code': result['code'],
            'explanation': result.get('explanation', '')
        })

    except Exception as e:
        logger.error(f"코드 수정 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _build_korean_prompt(user_input: str, language: str = None) -> str:
    """한글 최적화 프롬프트 구성"""
    lang_hint = f"언어: {language}" if language else ""

    return f"""당신은 한국어를 완벽하게 이해하는 코드 생성 AI입니다.

사용자 요청: {user_input}
{lang_hint}

규칙:
1. 한국어 요청을 정확히 이해하고 코드로 변환
2. 상세한 한글 주석 포함
3. 초보자도 이해할 수 있게 설명
4. 실행 가능한 완전한 코드 작성
5. 코드 블록(```)으로 감싸기

코드를 생성하세요:"""


def _build_modification_prompt(original_code: str, modification: str) -> str:
    """코드 수정 프롬프트 구성"""
    return f"""원본 코드:
```
{original_code}
```

수정 요청: {modification}

원본 코드를 수정한 새로운 코드를 생성하세요.
변경된 부분에는 # 수정됨 주석을 추가하세요.
"""
