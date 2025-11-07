"""컨텍스트 관리자"""
import json
from datetime import datetime
from pathlib import Path
from utils import print_info, print_success, get_project_root, ensure_dir

class ContextManager:
    """대화 이력 및 컨텍스트 관리"""
    
    def __init__(self, session_id=None):
        project_root = get_project_root()
        self.context_dir = project_root / "context"
        ensure_dir(self.context_dir)
        
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.session_id = session_id
        self.history = []
        self.session_file = self.context_dir / f"session_{self.session_id}.json"
        
        print_info(f"세션 ID: {self.session_id}")
    
    def add_interaction(self, user_message, assistant_response, metadata=None):
        """대화 이력 추가"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_response,
            'metadata': metadata or {}
        }
        self.history.append(interaction)
    
    def save_session(self):
        """세션 저장"""
        try:
            session_data = {
                'session_id': self.session_id,
                'created_at': datetime.now().isoformat(),
                'history': self.history
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print_success(f"세션 저장: {self.session_file.name}")
            return self.session_file
        except Exception as e:
            print(f"세션 저장 실패: {e}")
            raise
    
    def get_context(self, max_interactions=5):
        """최근 대화 이력 반환"""
        if not self.history:
            return ""
        
        recent_history = self.history[-max_interactions:]
        context_lines = ["이전 대화:"]
        
        for interaction in recent_history:
            user_msg = interaction['user']
            assistant_msg = interaction['assistant']
            context_lines.append(f"\n사용자: {user_msg}")
            context_lines.append(f"AI: {assistant_msg[:100]}...")
        
        return "\n".join(context_lines)
