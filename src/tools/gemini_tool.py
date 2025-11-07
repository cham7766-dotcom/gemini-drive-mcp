"""Gemini 코드 생성 Tool"""
from typing import Dict, Any
from src.clients.gemini_client import GeminiClient


class GeminiTool:
    """Gemini AI 코드 생성 MCP Tool"""

    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """
        Tool 정의 반환 (MCP 스키마)

        Returns:
            Dict: Tool 정의
        """
        return {
            "name": "generate_code",
            "description": "Gemini AI를 사용하여 코드를 생성합니다. 자연어로 원하는 코드를 요청하면 해당 프로그래밍 언어로 코드를 생성합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "코드 생성 요청 (자연어). 예: 'Python으로 피보나치 수열 생성하는 함수'"
                    },
                    "language": {
                        "type": "string",
                        "description": "프로그래밍 언어 (선택). 예: python, javascript, java 등",
                        "enum": ["python", "javascript", "typescript", "java", "cpp", "go", "rust", "ruby", "php"]
                    },
                    "context_id": {
                        "type": "string",
                        "description": "이전 컨텍스트 세션 ID (선택). 이전 대화를 참조하여 코드를 생성합니다."
                    }
                },
                "required": ["prompt"]
            }
        }

    @staticmethod
    async def execute(
        gemini_client: GeminiClient,
        context_manager: Any,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tool 실행

        Args:
            gemini_client: Gemini API 클라이언트
            context_manager: 컨텍스트 매니저
            arguments: Tool 인자
                - prompt: 코드 생성 요청
                - language: 프로그래밍 언어 (선택)
                - context_id: 세션 ID (선택)

        Returns:
            Dict: 실행 결과
            {
                "code": "생성된 코드",
                "language": "감지된 언어",
                "explanation": "코드 설명",
                "session_id": "현재 세션 ID"
            }

        Raises:
            ValueError: 필수 인자가 없는 경우
            Exception: 코드 생성 실패 시
        """
        # 인자 검증
        prompt = arguments.get("prompt")
        if not prompt:
            raise ValueError("'prompt' 인자가 필요합니다.")

        language = arguments.get("language")
        context_id = arguments.get("context_id")

        # 컨텍스트 로드 (있는 경우)
        context = None
        if context_id:
            try:
                # 기존 세션 로드
                temp_manager = type(context_manager)(session_id=context_id)
                temp_manager.load_session(context_id)
                context = temp_manager.get_context()
            except Exception:
                # 세션을 찾을 수 없으면 무시
                pass

        # 코드 생성
        result = await gemini_client.generate_code(
            prompt=prompt,
            language=language,
            context=context
        )

        # 컨텍스트에 저장
        context_manager.add_interaction(
            user_message=prompt,
            assistant_response=result["code"],
            metadata={
                "language": result["language"],
                "tool": "generate_code"
            }
        )
        context_manager.save_session()

        # 결과 반환
        return {
            "code": result["code"],
            "language": result["language"],
            "explanation": result["explanation"],
            "session_id": context_manager.session_id
        }
