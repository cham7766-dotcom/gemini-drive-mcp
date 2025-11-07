"""빠른 통합 테스트"""
import sys
import os
import asyncio
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.clients.gemini_client import GeminiClient
from src.managers.context_manager import ContextManager
from src.utils.config import Config


async def test_gemini_client():
    """Gemini 클라이언트 테스트"""
    print("\n=== Gemini Client 테스트 ===")

    try:
        config = Config()
        api_key = config.get_gemini_api_key()

        if not api_key:
            print("❌ Gemini API 키가 설정되지 않았습니다.")
            return False

        print("✓ API 키 로드 성공")

        # 클라이언트 초기화
        client = GeminiClient(api_key)
        print("✓ Gemini 클라이언트 초기화 성공")

        # 간단한 코드 생성 테스트
        print("\n코드 생성 테스트 중...")
        result = await client.generate_code(
            prompt="Python으로 'Hello World'를 출력하는 함수",
            language="python"
        )

        print(f"✓ 코드 생성 성공!")
        print(f"  언어: {result['language']}")
        print(f"  코드 길이: {len(result['code'])} 문자")
        print(f"\n생성된 코드:\n{result['code'][:200]}...")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_context_manager():
    """Context Manager 테스트"""
    print("\n=== Context Manager 테스트 ===")

    try:
        manager = ContextManager()
        print(f"✓ Context Manager 초기화 성공 (세션: {manager.session_id})")

        # 대화 추가
        manager.add_interaction(
            user_message="테스트 요청",
            assistant_response="테스트 응답"
        )
        print("✓ 대화 이력 추가 성공")

        # 세션 저장
        file_path = manager.save_session()
        print(f"✓ 세션 저장 성공: {file_path.name}")

        # 컨텍스트 조회
        context = manager.get_context()
        print(f"✓ 컨텍스트 조회 성공 ({len(context)} 문자)")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_config():
    """Config 테스트"""
    print("\n=== Config 테스트 ===")

    try:
        config = Config()
        print("✓ Config 초기화 성공")

        # 설정 값 확인
        api_key = config.get_gemini_api_key()
        print(f"✓ Gemini API Key: {api_key[:20]}..." if api_key else "❌ API Key 없음")

        creds_path = config.get_credentials_path()
        print(f"✓ Credentials 경로: {creds_path}")
        print(f"  파일 존재: {creds_path.exists()}")

        folder_name = config.get_drive_folder_name()
        print(f"✓ Drive 폴더: {folder_name}")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("Gemini-Drive MCP 빠른 테스트")
    print("=" * 60)

    results = []

    # Config 테스트
    results.append(("Config", await test_config()))

    # Context Manager 테스트
    results.append(("Context Manager", await test_context_manager()))

    # Gemini Client 테스트
    results.append(("Gemini Client", await test_gemini_client()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    for name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n총 {total}개 테스트 중 {passed}개 통과")

    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
