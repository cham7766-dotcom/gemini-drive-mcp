"""컨텍스트 관리 Tool"""
from typing import Dict, Any
from src.managers.context_manager import ContextManager


class ContextTool:
    """컨텍스트 관리 MCP Tool"""

    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Tool 정의 반환"""
        return {
            "name": "get_context",
            "description": "이전 작업 컨텍스트를 조회합니다. 이전 대화 내역과 생성된 코드를 확인할 수 있습니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "조회할 세션 ID (선택). 없으면 현재 세션"
                    },
                    "max_items": {
                        "type": "number",
                        "description": "최대 항목 수 (기본: 5)",
                        "default": 5
                    }
                }
            }
        }

    @staticmethod
    def get_list_sessions_definition() -> Dict[str, Any]:
        """세션 목록 조회 Tool 정의"""
        return {
            "name": "list_sessions",
            "description": "저장된 모든 세션 목록을 조회합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }

    @staticmethod
    async def execute(
        context_manager: ContextManager,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        컨텍스트 조회 실행

        Args:
            context_manager: 컨텍스트 매니저
            arguments: Tool 인자

        Returns:
            Dict: 컨텍스트 정보
        """
        session_id = arguments.get("session_id")
        max_items = arguments.get("max_items", 5)

        # 다른 세션 조회
        if session_id and session_id != context_manager.session_id:
            try:
                temp_manager = ContextManager(session_id=session_id)
                temp_manager.load_session(session_id)
                context_text = temp_manager.get_context(max_interactions=max_items)
                summary = temp_manager.get_summary()

                return {
                    "success": True,
                    "session_id": session_id,
                    "context": context_text,
                    "summary": summary,
                    "message": f"세션 {session_id}의 컨텍스트를 불러왔습니다."
                }
            except Exception as e:
                raise Exception(f"세션 로드 실패: {str(e)}")

        # 현재 세션 조회
        context_text = context_manager.get_context(max_interactions=max_items)
        summary = context_manager.get_summary()

        return {
            "success": True,
            "session_id": context_manager.session_id,
            "context": context_text,
            "summary": summary,
            "message": "현재 세션의 컨텍스트입니다."
        }

    @staticmethod
    async def list_sessions(context_manager: ContextManager) -> Dict[str, Any]:
        """
        세션 목록 조회 실행

        Args:
            context_manager: 컨텍스트 매니저

        Returns:
            Dict: 세션 목록
        """
        sessions = context_manager.list_sessions()

        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions,
            "message": f"{len(sessions)}개의 세션을 찾았습니다."
        }
