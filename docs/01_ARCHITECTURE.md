# MCP 서버 아키텍처 설계 🏗️

## 개요
Gemini-Drive MCP 서버의 기술적 아키텍처 및 구현 방식을 정의합니다.

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop / VS Code                  │
│                     (MCP Client)                             │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol (stdio)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  MCP Server (Python)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Tool Handlers                            │   │
│  │  ┌─────────────┬──────────────┬────────────────┐     │   │
│  │  │ Gemini Tool │ Drive Tool   │ Context Tool   │     │   │
│  │  └──────┬──────┴──────┬───────┴────────┬───────┘     │   │
│  └─────────┼─────────────┼────────────────┼─────────────┘   │
│            │             │                │                  │
│  ┌─────────▼─────────────▼────────────────▼─────────────┐   │
│  │              Service Layer                            │   │
│  │  ┌──────────────┬──────────────┬─────────────────┐   │   │
│  │  │GeminiClient  │DriveClient   │ContextManager   │   │   │
│  │  └──────┬───────┴──────┬───────┴─────────┬───────┘   │   │
│  └─────────┼──────────────┼─────────────────┼───────────┘   │
└────────────┼──────────────┼─────────────────┼───────────────┘
             │              │                 │
      ┌──────▼───────┐ ┌───▼─────────┐  ┌───▼──────┐
      │ Gemini API   │ │ Drive API   │  │ Local    │
      │              │ │             │  │ Storage  │
      └──────────────┘ └─────────────┘  └──────────┘
```

## 핵심 컴포넌트

### 1. MCP Server (`src/mcp_server.py`)

**역할**: MCP 프로토콜 구현 및 Claude Desktop과의 통신

**구조**:
```python
class GeminiDriveMCPServer:
    """
    MCP 서버 메인 클래스
    - stdio 통신으로 Claude Desktop과 연결
    - Tool 등록 및 요청 라우팅
    """

    def __init__(self):
        # MCP 서버 초기화
        # Tool 등록
        # 클라이언트 초기화

    async def handle_list_tools(self):
        # 사용 가능한 Tool 목록 반환

    async def handle_call_tool(self, tool_name, arguments):
        # Tool 실행 및 결과 반환
```

**주요 메서드**:
- `register_tools()`: MCP Tools 등록
- `handle_list_tools()`: Tool 목록 제공
- `handle_call_tool()`: Tool 실행
- `run()`: 서버 시작 (stdio 통신)

### 2. MCP Tools (`src/tools/`)

#### 2.1 Gemini Tool (`gemini_tool.py`)

```python
class GeminiTool:
    """Gemini AI 코드 생성 Tool"""

    @staticmethod
    def get_definition():
        return {
            "name": "generate_code",
            "description": "Gemini AI를 사용하여 코드 생성",
            "parameters": {
                "prompt": "코드 생성 요청 (자연어)",
                "language": "프로그래밍 언어 (선택)",
                "context_id": "이전 컨텍스트 ID (선택)"
            }
        }

    @staticmethod
    async def execute(gemini_client, arguments):
        # 1. 프롬프트 구성
        # 2. Gemini API 호출
        # 3. 코드 추출 및 반환
        # 4. 컨텍스트 저장
```

#### 2.2 Drive Tool (`drive_tool.py`)

```python
class DriveTool:
    """Google Drive 파일 관리 Tool"""

    @staticmethod
    def get_save_definition():
        return {
            "name": "save_to_drive",
            "description": "Google Drive에 파일 저장",
            "parameters": {
                "content": "파일 내용",
                "filename": "파일 이름",
                "folder": "폴더 이름 (선택)"
            }
        }

    @staticmethod
    def get_read_definition():
        return {
            "name": "read_from_drive",
            "description": "Google Drive에서 파일 읽기",
            "parameters": {
                "file_id": "파일 ID 또는 파일 이름"
            }
        }

    @staticmethod
    async def save_file(drive_client, arguments):
        # 1. 파일 생성
        # 2. Drive에 업로드
        # 3. 파일 ID 반환

    @staticmethod
    async def read_file(drive_client, arguments):
        # 1. 파일 검색
        # 2. 파일 다운로드
        # 3. 내용 반환
```

#### 2.3 Context Tool (`context_tool.py`)

```python
class ContextTool:
    """컨텍스트 관리 Tool"""

    @staticmethod
    def get_definition():
        return {
            "name": "get_context",
            "description": "이전 작업 컨텍스트 조회",
            "parameters": {
                "session_id": "세션 ID (선택)",
                "max_items": "최대 항목 수 (기본: 5)"
            }
        }

    @staticmethod
    async def execute(context_manager, arguments):
        # 1. 세션 이력 조회
        # 2. 포맷팅
        # 3. 반환
```

### 3. API Clients (`src/clients/`)

#### 3.1 Gemini Client (`gemini_client.py`)

**기존 코드 재사용 가능** - 약간의 수정 필요

```python
class GeminiClient:
    """Gemini API 클라이언트"""

    def __init__(self, api_key: str):
        # Gemini API 초기화

    async def generate_code(
        self,
        prompt: str,
        language: str = None,
        context: str = None
    ) -> dict:
        """
        코드 생성

        Returns:
            {
                "code": "생성된 코드",
                "language": "감지된 언어",
                "explanation": "코드 설명"
            }
        """

    def _build_prompt(self, prompt, language, context):
        # 프롬프트 구성

    def _extract_code(self, response_text):
        # 코드 블록 추출
```

#### 3.2 Drive Client (`drive_client.py`)

**새로 구현 필요**

```python
class DriveClient:
    """Google Drive API 클라이언트"""

    def __init__(self, credentials_path: str):
        # OAuth 인증 및 Drive API 초기화

    async def create_folder(self, folder_name: str) -> str:
        """폴더 생성 또는 기존 폴더 ID 반환"""

    async def upload_file(
        self,
        content: str,
        filename: str,
        folder_id: str = None,
        mime_type: str = "text/plain"
    ) -> dict:
        """
        파일 업로드

        Returns:
            {
                "file_id": "업로드된 파일 ID",
                "file_name": "파일 이름",
                "web_view_link": "웹 링크"
            }
        """

    async def download_file(self, file_id: str) -> str:
        """파일 다운로드 및 내용 반환"""

    async def list_files(
        self,
        folder_id: str = None,
        query: str = None
    ) -> list:
        """파일 목록 조회"""

    async def search_file(self, filename: str) -> dict:
        """파일 이름으로 검색"""
```

### 4. Managers (`src/managers/`)

#### 4.1 Context Manager (`context_manager.py`)

**기존 코드 재사용 가능** - 일부 개선

```python
class ContextManager:
    """컨텍스트 및 세션 관리"""

    def __init__(self, session_id: str = None):
        # 세션 초기화

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        metadata: dict = None
    ):
        """대화 이력 추가"""

    def save_session(self) -> str:
        """세션 저장 및 파일 경로 반환"""

    def load_session(self, session_id: str):
        """세션 로드"""

    def get_context(self, max_interactions: int = 5) -> str:
        """최근 컨텍스트 반환"""

    def get_summary(self) -> dict:
        """세션 요약 정보 반환"""
```

### 5. Utilities (`src/utils/`)

#### 5.1 Config (`config.py`)

```python
class Config:
    """환경 설정 관리"""

    @staticmethod
    def load_env():
        """환경 변수 로드"""

    @staticmethod
    def get_gemini_api_key() -> str:
        """Gemini API 키 반환"""

    @staticmethod
    def get_credentials_path() -> str:
        """Google OAuth 인증 파일 경로"""

    @staticmethod
    def get_drive_folder_name() -> str:
        """기본 Drive 폴더 이름"""
```

#### 5.2 Logger (`logger.py`)

```python
def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """로거 설정"""
```

## 통신 프로토콜

### MCP Protocol Flow

```
Claude Desktop → MCP Server
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_code",
    "arguments": {
      "prompt": "Python으로 피보나치 수열 생성하는 함수",
      "language": "python"
    }
  },
  "id": 1
}

MCP Server → Claude Desktop
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "생성된 코드:\n```python\ndef fibonacci(n):\n    ...\n```"
      }
    ]
  },
  "id": 1
}
```

## 에러 처리

### 에러 타입
1. **API 에러**: Gemini/Drive API 호출 실패
2. **인증 에러**: OAuth 토큰 만료
3. **파라미터 에러**: 잘못된 Tool 인자
4. **네트워크 에러**: 연결 실패

### 에러 응답 형식
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "error_type": "GeminiAPIError",
      "details": "API quota exceeded"
    }
  },
  "id": 1
}
```

## 성능 고려사항

### 1. 비동기 처리
- 모든 API 호출은 `async/await` 사용
- Drive 업로드는 백그라운드 처리 고려

### 2. 캐싱
- Drive 파일 목록 캐싱 (5분)
- 컨텍스트 메모리 캐싱

### 3. Rate Limiting
- Gemini API: 60 requests/minute
- Drive API: 1000 requests/100 seconds

## 보안

### 1. 인증 정보 관리
- API 키: `.env` 파일 (Git 제외)
- OAuth 토큰: `token.json` (자동 생성, Git 제외)

### 2. 파일 권한
- Drive 파일: 사용자만 접근 가능
- 로컬 세션: 읽기 전용

### 3. 입력 검증
- 파일 이름: 특수 문자 필터링
- 프롬프트: 최대 길이 제한

## 테스트 전략

### 1. 단위 테스트
- 각 Client 개별 테스트
- Mock API 사용

### 2. 통합 테스트
- Tool 실행 테스트
- 실제 API 호출 (테스트 계정)

### 3. E2E 테스트
- Claude Desktop 연동 테스트

## 다음 단계

1. **기존 코드 분석** → 재사용 가능한 부분 식별
2. **MCP 라이브러리 조사** → Python MCP SDK 확인
3. **Drive Client 구현** → OAuth 및 파일 업로드
4. **MCP Server 구현** → Tool 등록 및 통신
5. **통합 테스트** → Claude Desktop 연동

---

**마지막 업데이트**: 2025-11-07
**다음 문서**: [03_IMPLEMENTATION.md](03_IMPLEMENTATION.md)
