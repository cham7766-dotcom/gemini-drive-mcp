# 웹 UI 아키텍처 설계 🖥️

## 개요
사용자가 한글로 명령을 입력하면 Gemini가 코드를 생성하고, 결과를 시각화하는 웹 인터페이스

## 사용자 워크플로우

```
1. 사용자: 웹 브라우저 접속
   ↓
2. 한글로 요청 입력: "Python으로 피보나치 수열 만들어줘"
   ↓
3. Gemini AI가 코드 생성
   ↓
4. 생성된 코드를 화면에 표시
   ↓
5. [저장] 버튼 클릭 → Google Drive에 자동 저장
   ↓
6. 저장된 파일 목록 확인
   ↓
7. 이전 코드 불러와서 수정 요청
```

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────┐
│         웹 브라우저 (사용자)                       │
│  ┌──────────────────────────────────────────┐   │
│  │  입력: "Python으로 계산기 만들어줘"        │   │
│  │  [생성] 버튼                              │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  생성된 코드 (Syntax Highlight)           │   │
│  │  def calculator():                        │   │
│  │      # 코드...                            │   │
│  │  [저장] [수정 요청] [복사]                │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  저장된 파일 목록                          │   │
│  │  □ calculator.py                          │   │
│  │  □ fibonacci.py                           │   │
│  └──────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────┘
             │ HTTP/WebSocket
             ▼
┌─────────────────────────────────────────────────┐
│         Flask 웹 서버                            │
│  ┌──────────────────────────────────────────┐   │
│  │  API Endpoints:                           │   │
│  │  POST /api/generate  - 코드 생성          │   │
│  │  POST /api/save      - Drive 저장         │   │
│  │  GET  /api/files     - 파일 목록          │   │
│  │  GET  /api/file/:id  - 파일 읽기         │   │
│  │  POST /api/modify    - 코드 수정 요청    │   │
│  └──────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│    기존 MCP 컴포넌트 재사용                      │
│  ┌──────────────┬──────────────┬────────────┐   │
│  │GeminiClient  │DriveClient   │ContextMgr  │   │
│  └──────────────┴──────────────┴────────────┘   │
└─────────────────────────────────────────────────┘
```

## 화면 구성

### 메인 화면
```html
┌────────────────────────────────────────────┐
│  Gemini Code Generator                     │
├────────────────────────────────────────────┤
│                                            │
│  💬 무엇을 만들까요? (한글로 입력하세요)    │
│  ┌────────────────────────────────────┐   │
│  │ Python으로 피보나치 수열 만들기     │   │
│  └────────────────────────────────────┘   │
│           [🚀 코드 생성]                   │
│                                            │
├────────────────────────────────────────────┤
│  📝 생성된 코드:                           │
│  ┌────────────────────────────────────┐   │
│  │ def fibonacci(n):                   │   │
│  │     """피보나치 수열 생성"""         │   │
│  │     if n <= 1:                      │   │
│  │         return n                    │   │
│  │     return fib(n-1) + fib(n-2)     │   │
│  └────────────────────────────────────┘   │
│  [💾 Drive 저장] [📋 복사] [✏️ 수정]     │
│                                            │
├────────────────────────────────────────────┤
│  📂 저장된 파일 (Google Drive)             │
│  ┌────────────────────────────────────┐   │
│  │ □ fibonacci.py      (방금 전)       │   │
│  │ □ calculator.py     (1시간 전)      │   │
│  │ □ hello.py          (어제)          │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## 기술 스택

### Backend (Flask)
```python
Flask>=3.0.0          # 웹 프레임워크
Flask-CORS>=4.0.0     # CORS 처리
Flask-SocketIO>=5.3.0 # 실시간 통신 (선택)
```

### Frontend
```
- HTML5 / CSS3
- JavaScript (Vanilla 또는 Vue.js/React)
- Prism.js / Highlight.js (코드 하이라이팅)
- Tailwind CSS (스타일링)
```

## API 설계

### 1. 코드 생성
```http
POST /api/generate
Content-Type: application/json

Request:
{
  "prompt": "Python으로 피보나치 수열 만들어줘",
  "language": "python"  // 선택
}

Response:
{
  "success": true,
  "code": "def fibonacci(n): ...",
  "language": "python",
  "explanation": "이 코드는 재귀로...",
  "session_id": "20251107_143857"
}
```

### 2. Drive에 저장
```http
POST /api/save
Content-Type: application/json

Request:
{
  "code": "def fibonacci(n): ...",
  "filename": "fibonacci.py",
  "folder": "GeminiCodeGeneration"  // 선택
}

Response:
{
  "success": true,
  "file_id": "1abc...",
  "web_view_link": "https://drive.google.com/..."
}
```

### 3. 파일 목록 조회
```http
GET /api/files?folder=GeminiCodeGeneration

Response:
{
  "success": true,
  "files": [
    {
      "id": "1abc...",
      "name": "fibonacci.py",
      "created_at": "2025-11-07T14:38:57",
      "web_view_link": "https://..."
    }
  ]
}
```

### 4. 파일 읽기
```http
GET /api/file/1abc...

Response:
{
  "success": true,
  "filename": "fibonacci.py",
  "content": "def fibonacci(n): ...",
  "language": "python"
}
```

### 5. 코드 수정 요청
```http
POST /api/modify
Content-Type: application/json

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
```

## 프로젝트 구조 확장

```
gemini-drive-mcp/
├── src/
│   ├── web/                    # 🆕 웹 애플리케이션
│   │   ├── __init__.py
│   │   ├── app.py              # Flask 앱
│   │   ├── api/                # API 라우트
│   │   │   ├── __init__.py
│   │   │   ├── generate.py    # 코드 생성 API
│   │   │   ├── drive.py        # Drive 관련 API
│   │   │   └── files.py        # 파일 관리 API
│   │   └── static/             # 정적 파일
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── js/
│   │       │   └── app.js
│   │       └── index.html
│   │
│   ├── mcp_server.py           # 기존 MCP 서버
│   ├── clients/                # 재사용
│   ├── managers/               # 재사용
│   ├── tools/                  # 재사용
│   └── utils/                  # 재사용
```

## 실행 방법

### 1. 웹 서버 모드
```bash
python src/web/app.py
# http://localhost:5000 접속
```

### 2. MCP 서버 모드 (Claude Desktop)
```bash
python src/mcp_server.py
```

## 구현 우선순위

### Phase 1: 기본 웹 UI (1일)
- [ ] Flask 앱 구조 생성
- [ ] 코드 생성 API 구현
- [ ] 간단한 HTML 인터페이스
- [ ] 코드 하이라이팅

### Phase 2: Drive 연동 (1일)
- [ ] Drive 저장 API
- [ ] 파일 목록 조회 API
- [ ] 파일 읽기 API

### Phase 3: UI 개선 (1일)
- [ ] 반응형 디자인
- [ ] 로딩 인디케이터
- [ ] 에러 처리
- [ ] 코드 복사 기능

### Phase 4: 고급 기능 (1일)
- [ ] 코드 수정 요청
- [ ] 세션 관리
- [ ] 파일 검색
- [ ] 다운로드 기능

## 컨텍스트 엔지니어링 전략

### 1. 프롬프트 최적화
사용자의 한글 입력을 Gemini가 잘 이해하도록:

```python
def build_korean_prompt(user_input: str) -> str:
    return f"""
당신은 한국어를 완벽하게 이해하는 코드 생성 AI입니다.

사용자 요청: {user_input}

규칙:
1. 한국어 요청을 정확히 이해하고 코드로 변환
2. 상세한 한글 주석 포함
3. 초보자도 이해할 수 있게 설명
4. 실행 가능한 완전한 코드 작성
5. 코드 블록(```)으로 감싸기

코드를 생성하세요:
"""
```

### 2. 컨텍스트 유지
이전 대화를 기억하여 연속 작업:

```python
def build_context_prompt(user_input: str, previous_code: str) -> str:
    return f"""
이전에 생성한 코드:
```python
{previous_code}
```

사용자의 새로운 요청: {user_input}

위 코드를 참고하여 요청을 처리하세요.
"""
```

### 3. 수정 요청 처리
```python
def build_modification_prompt(original_code: str, modification: str) -> str:
    return f"""
원본 코드:
```python
{original_code}
```

수정 요청: {modification}

원본 코드를 수정한 새로운 코드를 생성하세요.
변경된 부분에는 # 수정됨 주석을 추가하세요.
"""
```

## 다음 단계

1. Flask 웹 서버 구현
2. 프론트엔드 UI 구현
3. 기존 컴포넌트와 통합
4. 테스트 및 배포

---

**작성일**: 2025-11-07
**목표**: 사용자 친화적인 웹 인터페이스로 Gemini 코드 생성 서비스 제공
