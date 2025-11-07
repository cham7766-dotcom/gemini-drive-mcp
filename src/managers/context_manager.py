"""컨텍스트 관리자"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


class ContextManager:
    """대화 이력 및 컨텍스트 관리"""

    def __init__(self, session_id: Optional[str] = None, context_dir: Optional[Path] = None):
        """
        컨텍스트 관리자 초기화

        Args:
            session_id: 세션 ID (None이면 자동 생성)
            context_dir: 컨텍스트 저장 디렉토리 (None이면 기본 경로 사용)
        """
        if context_dir is None:
            project_root = Path(__file__).parent.parent.parent
            context_dir = project_root / "context"

        self.context_dir = context_dir
        self.context_dir.mkdir(parents=True, exist_ok=True)

        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.session_id = session_id
        self.history: List[Dict] = []
        self.session_file = self.context_dir / f"session_{self.session_id}.json"
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": None
        }

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ):
        """
        대화 이력 추가

        Args:
            user_message: 사용자 메시지
            assistant_response: AI 응답
            metadata: 추가 메타데이터 (선택)
        """
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_response,
            'metadata': metadata or {}
        }
        self.history.append(interaction)
        self.metadata["last_updated"] = datetime.now().isoformat()

    def save_session(self) -> Path:
        """
        세션 저장

        Returns:
            Path: 저장된 파일 경로

        Raises:
            Exception: 저장 실패 시
        """
        try:
            session_data = {
                'session_id': self.session_id,
                'metadata': self.metadata,
                'history': self.history
            }

            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            return self.session_file
        except Exception as e:
            raise Exception(f"세션 저장 실패: {e}")

    def load_session(self, session_id: str):
        """
        기존 세션 로드

        Args:
            session_id: 로드할 세션 ID

        Raises:
            FileNotFoundError: 세션 파일이 없는 경우
            Exception: 로드 실패 시
        """
        session_file = self.context_dir / f"session_{session_id}.json"

        if not session_file.exists():
            raise FileNotFoundError(f"세션 파일을 찾을 수 없습니다: {session_file}")

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            self.session_id = session_data['session_id']
            self.metadata = session_data.get('metadata', {})
            self.history = session_data['history']
            self.session_file = session_file
        except Exception as e:
            raise Exception(f"세션 로드 실패: {e}")

    def get_context(self, max_interactions: int = 5) -> str:
        """
        최근 대화 이력 반환

        Args:
            max_interactions: 반환할 최대 대화 수

        Returns:
            str: 포맷팅된 컨텍스트 문자열
        """
        if not self.history:
            return ""

        recent_history = self.history[-max_interactions:]
        context_lines = ["이전 대화:"]

        for interaction in recent_history:
            user_msg = interaction['user']
            assistant_msg = interaction['assistant']
            # 응답이 너무 길면 요약
            if len(assistant_msg) > 200:
                assistant_msg = assistant_msg[:200] + "..."

            context_lines.append(f"\n사용자: {user_msg}")
            context_lines.append(f"AI: {assistant_msg}")

        return "\n".join(context_lines)

    def get_summary(self) -> Dict:
        """
        세션 요약 정보 반환

        Returns:
            Dict: 세션 요약
        """
        return {
            "session_id": self.session_id,
            "created_at": self.metadata.get("created_at"),
            "last_updated": self.metadata.get("last_updated"),
            "total_interactions": len(self.history),
            "session_file": str(self.session_file)
        }

    def list_sessions(self) -> List[Dict]:
        """
        저장된 모든 세션 목록 반환

        Returns:
            List[Dict]: 세션 정보 리스트
        """
        sessions = []

        for session_file in self.context_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                sessions.append({
                    "session_id": data['session_id'],
                    "created_at": data.get('metadata', {}).get('created_at'),
                    "interactions": len(data['history']),
                    "file": str(session_file)
                })
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)

    def clear_history(self):
        """현재 세션의 대화 이력 초기화"""
        self.history = []
        self.metadata["last_updated"] = datetime.now().isoformat()
