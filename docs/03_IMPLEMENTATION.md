# 구현 계획 📝

## 개요
MCP 서버 구현을 위한 단계별 실행 계획 및 기존 코드 재사용 전략

## 기존 코드 분석

### 재사용 가능한 코드

#### 1. `src/gemini_client.py` ✅ 70% 재사용
**재사용 부분**:
- `GeminiClient.__init__()`: API 초기화
- `_build_prompt()`: 프롬프트 구성 로직
- `_extract_code()`: 코드 블록 추출

**수정 필요**:
- `generate_code()`: async 함수로 변경
- 반환 형식: 구조화된 딕셔너리로 변경

**수정 예시**:
```python
# Before
def generate_code(self, prompt, context=None):
    response = self.model.generate_content(full_prompt)
    return self._extract_code(response.text)

# After
async def generate_code(self, prompt, language=None, context=None):
    response = await self.model.generate_content_async(full_prompt)
    return {
        "code": self._extract_code(response.text),
        "language": language or self._detect_language(response.text),
        "explanation": self._extract_explanation(response.text)
    }
```

#### 2. `src/context_manager.py` ✅ 90% 재사용
**재사용 부분**:
- 전체 구조 그대로 사용 가능
- `add_interaction()`, `save_session()`, `get_context()` 모두 유효

**추가 필요**:
- `load_session()`: 기존 세션 로드 기능
- `get_summary()`: 세션 요약 정보

#### 3. `src/utils.py` ✅ 50% 재사용
**재사용 부분**:
- `setup_logging()`, `get_project_root()`, `ensure_dir()`

**분리 필요**:
- `print_*` 함수들 → 별도 파일로 분리 (MCP 서버에서 stdout 사용 불가)
- `load_config()` → `src/utils/config.py`로 이동 및 개선

### 새로 구현 필요한 코드

#### 1. `src/mcp_server.py` ⚠️ 완전 신규
MCP 프로토콜 구현

#### 2. `src/clients/drive_client.py` ⚠️ 완전 신규
Google Drive API 연동

#### 3. `src/tools/` ⚠️ 완전 신규
MCP Tool 구현

## 구현 단계

### Phase 1: 프로젝트 리팩토링 (1일)

#### 1.1 디렉토리 구조 재구성
```bash
# 백업
cp -r src src_backup

# 새 구조 생성
mkdir -p src/tools
mkdir -p src/clients
mkdir -p src/managers
mkdir -p src/utils
```

#### 1.2 기존 파일 이동 및 수정
```bash
# Gemini Client 이동
mv src/gemini_client.py src/clients/gemini_client.py

# Context Manager 이동
mv src/context_manager.py src/managers/context_manager.py

# Utils 분리
# - config 관련 → src/utils/config.py
# - logging 관련 → src/utils/logger.py
```

#### 1.3 requirements.txt 업데이트
```bash
# MCP SDK 추가
mcp>=0.1.0

# 기존 라이브러리 유지
google-generativeai>=0.3.0
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
python-dotenv>=1.0.0
```

### Phase 2: Drive Client 구현 (2일)

#### 2.1 OAuth 인증 구현
**파일**: `src/clients/drive_client.py`

```python
class DriveClient:
    def __init__(self, credentials_path: str):
        # 1. credentials.json 로드
        # 2. OAuth 플로우 실행 (처음 실행 시)
        # 3. token.json 저장
        # 4. Drive API 서비스 초기화
```

**테스트**:
```bash
python tests/test_drive_auth.py  # OAuth 인증 테스트
```

#### 2.2 파일 업로드 구현
```python
async def upload_file(
    self,
    content: str,
    filename: str,
    folder_id: str = None
) -> dict:
    # 1. 메타데이터 생성
    # 2. 파일 업로드
    # 3. 결과 반환
```

**테스트**:
```bash
python tests/test_drive_upload.py  # 파일 업로드 테스트
```

#### 2.3 파일 다운로드 및 검색 구현
```python
async def download_file(self, file_id: str) -> str
async def search_file(self, filename: str) -> dict
async def list_files(self, folder_id: str = None) -> list
```

**테스트**:
```bash
python tests/test_drive_operations.py  # 전체 작업 테스트
```

### Phase 3: MCP Server 기반 구축 (2일)

#### 3.1 MCP SDK 조사 및 선택
**옵션**:
1. Anthropic 공식 MCP Python SDK
2. 커뮤니티 구현체

**선택 기준**:
- stdio 통신 지원
- Tool 등록 간편성
- 비동기 지원

#### 3.2 기본 MCP Server 구현
**파일**: `src/mcp_server.py`

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("gemini-drive-mcp")

@app.list_tools()
async def list_tools():
    return [
        # Tool 정의 반환
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # Tool 실행
```

**테스트**:
```bash
python src/mcp_server.py  # 서버 시작 테스트
# Claude Desktop 없이 직접 JSON-RPC 전송
```

### Phase 4: MCP Tools 구현 (3일)

#### 4.1 Gemini Tool
**파일**: `src/tools/gemini_tool.py`

```python
from src.clients.gemini_client import GeminiClient

class GeminiTool:
    @staticmethod
    def get_definition():
        return {
            "name": "generate_code",
            "description": "...",
            "inputSchema": { ... }
        }

    @staticmethod
    async def execute(gemini_client, arguments):
        prompt = arguments["prompt"]
        language = arguments.get("language")
        result = await gemini_client.generate_code(prompt, language)
        return result
```

**테스트**:
```bash
python tests/test_gemini_tool.py
```

#### 4.2 Drive Tool
**파일**: `src/tools/drive_tool.py`

```python
class DriveTool:
    @staticmethod
    def get_save_definition(): ...

    @staticmethod
    def get_read_definition(): ...

    @staticmethod
    async def save_file(drive_client, arguments): ...

    @staticmethod
    async def read_file(drive_client, arguments): ...
```

**테스트**:
```bash
python tests/test_drive_tool.py
```

#### 4.3 Context Tool
**파일**: `src/tools/context_tool.py`

```python
class ContextTool:
    @staticmethod
    def get_definition(): ...

    @staticmethod
    async def execute(context_manager, arguments): ...
```

**테스트**:
```bash
python tests/test_context_tool.py
```

### Phase 5: 통합 및 테스트 (2일)

#### 5.1 MCP Server에 Tools 등록
```python
# src/mcp_server.py

from src.tools.gemini_tool import GeminiTool
from src.tools.drive_tool import DriveTool
from src.tools.context_tool import ContextTool

# Tools 등록
app.add_tool(GeminiTool.get_definition(), GeminiTool.execute)
app.add_tool(DriveTool.get_save_definition(), DriveTool.save_file)
# ...
```

#### 5.2 Claude Desktop 설정
**파일**: `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gemini-drive": {
      "command": "python",
      "args": [
        "c:\\Users\\chosun\\Desktop\\gemini-drive-mcp\\src\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "c:\\Users\\chosun\\Desktop\\gemini-drive-mcp"
      }
    }
  }
}
```

#### 5.3 통합 테스트 시나리오
```
1. Claude Desktop 시작
2. MCP 서버 인식 확인
3. Tool 목록 확인
4. generate_code 실행
5. save_to_drive 실행
6. read_from_drive 실행
7. 컨텍스트 기반 연속 작업
```

### Phase 6: 문서화 및 최적화 (1일)

#### 6.1 README 업데이트
- 설치 방법
- 설정 방법
- 사용 예시

#### 6.2 에러 처리 강화
- API 에러 핸들링
- 재시도 로직
- 사용자 친화적 에러 메시지

#### 6.3 로깅 개선
- 각 Tool 실행 로그
- API 호출 로그
- 에러 스택 트레이스

## 개발 체크리스트

### Week 1: 기반 구조
- [ ] 프로젝트 리팩토링 완료
- [ ] Drive Client OAuth 인증 구현
- [ ] Drive Client 기본 작업 구현
- [ ] 단위 테스트 작성

### Week 2: MCP 서버
- [ ] MCP Server 기본 구조 구현
- [ ] Gemini Tool 구현
- [ ] Drive Tool 구현
- [ ] Context Tool 구현
- [ ] 통합 테스트

### Week 3: 완성
- [ ] Claude Desktop 연동 테스트
- [ ] 버그 수정
- [ ] 문서 완성
- [ ] 배포 준비

## 리스크 및 대응

### 리스크 1: MCP SDK 미성숙
**대응**: stdio 직접 구현 준비

### 리스크 2: Drive API 할당량 초과
**대응**: Rate limiting 구현, 캐싱 전략

### 리스크 3: Gemini API 응답 불안정
**대응**: 재시도 로직, 타임아웃 설정

## 성공 기준

1. ✅ Claude Desktop에서 Tools 인식
2. ✅ 코드 생성 성공률 95% 이상
3. ✅ Drive 저장 성공률 99% 이상
4. ✅ 평균 응답 시간 < 5초
5. ✅ 에러 발생 시 명확한 메시지

---

**마지막 업데이트**: 2025-11-07
**다음 단계**: 기존 코드 리팩토링 시작
