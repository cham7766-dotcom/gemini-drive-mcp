"""설치 확인 테스트"""
import sys

def test_python_version():
    print("✓ Python 버전 확인...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python 3.8 이상 필요")
        return False

def test_imports():
    packages = {
        'google-generativeai': 'google.generativeai',
        'google-auth': 'google.auth',
        'python-dotenv': 'dotenv',
        'colorama': 'colorama'
    }
    
    all_ok = True
    for pkg_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {pkg_name}")
        except ImportError:
            print(f"  ❌ {pkg_name} 필요")
            all_ok = False
    return all_ok

def main():
    print("\n" + "="*60)
    print("🧪 Gemini Drive MCP 설치 테스트")
    print("="*60 + "\n")
    
    results = []
    
    print("📝 Python 버전 테스트:")
    results.append(test_python_version())
    
    print("\n📝 필수 패키지 테스트:")
    results.append(test_imports())
    
    print("\n" + "="*60)
    if all(results):
        print("🎉 모든 테스트 통과!")
        print("\n다음: docs/02_API_SETUP.md 참조")
    else:
        print("❌ 일부 테스트 실패")
        print("\n해결:")
        print("  1. pip install -r requirements.txt")
        print("  2. 가상 환경 활성화 확인")
    print("="*60 + "\n")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
