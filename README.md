# 🚀 Gemini-Drive MCP

**Gemini AI와 Google Drive를 연결하는 MCP(Model Context Protocol) 서버**

Claude Desktop에서 Gemini AI로 코드를 생성하고, 자동으로 Google Drive에 저장하며, 저장된 코드를 다시 읽어와 수정할 수 있는 통합 워크플로우를 제공합니다.

---

## ✨ 주요 기능

- 🤖 **AI 코드 생성**: Gemini AI를 활용한 자동 코드 생성
- 💾 **자동 저장**: 생성된 코드를 Google Drive에 자동 업로드
- 🔄 **컨텍스트 유지**: 이전 작업 내용을 기억하고 이어서 작업
- 📝 **상세한 주석**: 코딩 초보자도 이해할 수 있는 친절한 주석
- 🎯 **Claude Desktop 통합**: MCP 프로토콜을 통한 원활한 연동

---

## 📋 시작하기 전에

### 필수 요구사항
- Python 3.8 이상
- Google 계정
- Gemini API 키
- Google Cloud Console 계정

### 필요한 API
1. **Gemini API** - AI 코드 생성
2. **Google Drive API** - 파일 저장/관리

---

## 🔧 설치 방법

### 1단계: 프로젝트 다운로드
```bash
# 프로젝트 폴더를 원하는 위치에 배치
cd 경로/gemini-drive-mcp
```

### 2단계: 가상 환경 생성
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3단계: 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 4단계: API 설정
자세한 내용은 `docs/02_API_SETUP.md` 문서를 참조하세요.

1. Gemini API 키 발급
2. Google Drive API 활성화
3. OAuth 인증 정보 다운로드
4. `.env` 파일 설정

---

## 📁 프로젝트 구조

```
gemini-drive-mcp/
├── docs/                   # 📚 문서
│   ├── 00_PROJECT_CONTEXT.md
│   ├── 01_SETUP_GUIDE.md
│   └── 02_API_SETUP.md
├── src/                    # 💻 소스 코드
├── tests/                  # 🧪 테스트
├── config/                 # ⚙️ 설정
├── logs/                   # 📝 로그
└── requirements.txt        # 📦 패키지 목록
```

---

## 🚀 빠른 시작

### 설치 확인 테스트
```bash
python tests/test_installation.py
```

### 기본 사용법
```bash
# 메인 프로그램 실행
python src/main.py
```

---

## 📖 문서

프로젝트의 모든 문서는 `docs/` 폴더에 있습니다:

1. **00_PROJECT_CONTEXT.md** - 프로젝트 전체 개요 및 아키텍처
2. **01_SETUP_GUIDE.md** - 설치 및 환경 설정 가이드
3. **02_API_SETUP.md** - API 키 발급 및 설정 방법
4. **03_USAGE_GUIDE.md** - 사용법 가이드

---

## 🧪 테스트

```bash
# 설치 확인 테스트
python tests/test_installation.py

# 통합 테스트
python tests/test_integration.py
```

---

## 🔐 보안

- ⚠️ `.env` 파일과 `credentials.json`을 절대 Git에 올리지 마세요
- ⚠️ API 키를 다른 사람과 공유하지 마세요
- ✅ 모든 민감한 정보는 `.gitignore`에 포함되어 있습니다

---

## 🐛 문제 해결

문제가 발생하면 다음을 확인하세요:

1. Python 버전이 3.8 이상인가요?
2. 모든 라이브러리가 설치되었나요?
3. `.env` 파일이 올바르게 설정되었나요?
4. API 키가 유효한가요?

자세한 내용은 각 문서의 "문제 해결" 섹션을 참조하세요.

---

## 📝 개발 로그

개발 진행 상황은 `docs/04_DEVELOPMENT_LOG.md`에서 확인할 수 있습니다.

---

## 👥 기여

이 프로젝트는 개인 프로젝트입니다. 피드백과 제안은 언제나 환영합니다!

---

## 🙏 감사의 말

- Google Gemini AI
- Google Drive API
- Python 커뮤니티

---

**작성일**: 2025-11-06  
**버전**: v1.0.0
