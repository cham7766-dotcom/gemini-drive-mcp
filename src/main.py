"""메인 프로그램"""
import sys
import os

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from utils import setup_logging, load_config, print_error, print_info, print_success
from gemini_client import GeminiClient
from context_manager import ContextManager

class GeminiDriveMCP:
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("🚀 Gemini Drive MCP 시작")
        print("="*60 + "\n")
        
        self.config = load_config()
        self.logger = setup_logging(self.config.get("LOG_FILE", "logs/app.log"))
        
        api_key = self.config.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        self.gemini_client = GeminiClient(api_key)
        self.context_manager = ContextManager()
        
        print_success("모든 시스템 준비 완료!\n")
    
    def generate_code(self, user_request):
        """코드 생성"""
        context = self.context_manager.get_context()
        code = self.gemini_client.generate_code(user_request, context)
        
        self.context_manager.add_interaction(user_request, code)
        self.context_manager.save_session()
        
        return code
    
    def interactive_mode(self):
        """대화형 모드"""
        print("="*60)
        print("📝 대화형 모드 (종료: exit)")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\n💡 요청: ").strip()
                
                if user_input.lower() in ['exit', '종료']:
                    print_info("종료합니다...")
                    break
                
                if not user_input:
                    continue
                
                code = self.generate_code(user_input)
                print(f"\n생성된 코드:\n{code}\n")
                
            except KeyboardInterrupt:
                print("\n종료합니다...")
                break
            except Exception as e:
                print_error(f"오류: {str(e)}")
        
        print("\n👋 감사합니다!\n")

def main():
    """프로그램 진입점"""
    try:
        mcp = GeminiDriveMCP()
        mcp.interactive_mode()
    except Exception as e:
        print_error(f"시작 실패: {str(e)}")
        print_info("config/.env 파일에 GEMINI_API_KEY를 설정하세요")
        sys.exit(1)

if __name__ == "__main__":
    main()
