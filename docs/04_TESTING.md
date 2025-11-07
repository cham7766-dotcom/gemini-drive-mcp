# 테스트 계획 🧪

## 개요
MCP 서버의 신뢰성과 안정성을 보장하기 위한 체계적인 테스트 전략

## 테스트 레벨

### 1. 단위 테스트 (Unit Tests)
개별 컴포넌트의 기능 검증

### 2. 통합 테스트 (Integration Tests)
컴포넌트 간 상호작용 검증

### 3. E2E 테스트 (End-to-End Tests)
Claude Desktop과의 전체 워크플로우 검증

## 테스트 구조

```
tests/
├── unit/                          # 단위 테스트
│   ├── test_gemini_client.py
│   ├── test_drive_client.py
│   ├── test_context_manager.py
│   └── test_utils.py
│
├── integration/                   # 통합 테스트
│   ├── test_gemini_tool.py
│   ├── test_drive_tool.py
│   ├── test_context_tool.py
│   └── test_mcp_server.py
│
├── e2e/                           # E2E 테스트
│   ├── test_claude_integration.py
│   └── test_workflows.py
│
├── fixtures/                      # 테스트 데이터
│   ├── sample_code.py
│   ├── mock_responses.json
│   └── test_credentials.json
│
└── conftest.py                    # Pytest 설정
```

## 단위 테스트

### 1. Gemini Client 테스트
**파일**: `tests/unit/test_gemini_client.py`

```python
import pytest
from unittest.mock import Mock, patch
from src.clients.gemini_client import GeminiClient

class TestGeminiClient:
    @pytest.fixture
    def client(self):
        return GeminiClient(api_key="test_key")

    @pytest.mark.asyncio
    async def test_generate_code_success(self, client):
        """코드 생성 성공 테스트"""
        with patch.object(client.model, 'generate_content_async') as mock:
            mock.return_value.text = "```python\nprint('Hello')\n```"

            result = await client.generate_code("print hello")

            assert result["code"] == "print('Hello')"
            assert result["language"] == "python"
            assert "code" in result

    @pytest.mark.asyncio
    async def test_generate_code_with_context(self, client):
        """컨텍스트 포함 코드 생성 테스트"""
        context = "이전에 hello 함수를 만들었습니다"
        result = await client.generate_code(
            "goodbye 함수도 만들어줘",
            context=context
        )
        assert result is not None

    def test_build_prompt(self, client):
        """프롬프트 구성 테스트"""
        prompt = client._build_prompt(
            "make a function",
            language="python",
            context="previous code"
        )
        assert "make a function" in prompt
        assert "python" in prompt.lower()
        assert "previous code" in prompt

    def test_extract_code(self, client):
        """코드 추출 테스트"""
        response = "Here is code:\n```python\nprint('test')\n```\nExplanation..."
        code = client._extract_code(response)
        assert code == "print('test')"

    def test_extract_code_without_markers(self, client):
        """코드 마커 없는 응답 처리"""
        response = "print('test')"
        code = client._extract_code(response)
        assert code == "print('test')"
```

### 2. Drive Client 테스트
**파일**: `tests/unit/test_drive_client.py`

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.clients.drive_client import DriveClient

class TestDriveClient:
    @pytest.fixture
    def client(self):
        with patch('src.clients.drive_client.build') as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            return DriveClient(credentials_path="test_creds.json")

    @pytest.mark.asyncio
    async def test_upload_file(self, client):
        """파일 업로드 테스트"""
        result = await client.upload_file(
            content="test content",
            filename="test.py"
        )

        assert "file_id" in result
        assert result["file_name"] == "test.py"
        assert "web_view_link" in result

    @pytest.mark.asyncio
    async def test_download_file(self, client):
        """파일 다운로드 테스트"""
        with patch.object(client.service.files(), 'get_media') as mock:
            mock.return_value.execute.return_value = b"file content"

            content = await client.download_file("file_id_123")

            assert content == "file content"

    @pytest.mark.asyncio
    async def test_search_file(self, client):
        """파일 검색 테스트"""
        with patch.object(client.service.files(), 'list') as mock:
            mock.return_value.execute.return_value = {
                "files": [{
                    "id": "123",
                    "name": "test.py"
                }]
            }

            result = await client.search_file("test.py")

            assert result["id"] == "123"
            assert result["name"] == "test.py"

    @pytest.mark.asyncio
    async def test_create_folder(self, client):
        """폴더 생성 테스트"""
        folder_id = await client.create_folder("TestFolder")
        assert folder_id is not None
```

### 3. Context Manager 테스트
**파일**: `tests/unit/test_context_manager.py`

```python
import pytest
import json
from pathlib import Path
from src.managers.context_manager import ContextManager

class TestContextManager:
    @pytest.fixture
    def manager(self, tmp_path):
        # 임시 디렉토리 사용
        with patch('src.managers.context_manager.get_project_root') as mock:
            mock.return_value = tmp_path
            return ContextManager()

    def test_add_interaction(self, manager):
        """대화 이력 추가 테스트"""
        manager.add_interaction(
            user_message="test request",
            assistant_response="test response"
        )

        assert len(manager.history) == 1
        assert manager.history[0]["user"] == "test request"

    def test_save_session(self, manager, tmp_path):
        """세션 저장 테스트"""
        manager.add_interaction("msg1", "resp1")
        file_path = manager.save_session()

        assert file_path.exists()
        with open(file_path, 'r') as f:
            data = json.load(f)
            assert len(data["history"]) == 1

    def test_load_session(self, manager, tmp_path):
        """세션 로드 테스트"""
        # 세션 저장
        manager.add_interaction("msg1", "resp1")
        manager.save_session()

        # 새 매니저로 로드
        new_manager = ContextManager(session_id=manager.session_id)
        new_manager.load_session(manager.session_id)

        assert len(new_manager.history) == 1

    def test_get_context(self, manager):
        """컨텍스트 조회 테스트"""
        for i in range(10):
            manager.add_interaction(f"msg{i}", f"resp{i}")

        context = manager.get_context(max_interactions=5)

        assert "msg9" in context
        assert "msg4" not in context  # 5개만 포함
```

## 통합 테스트

### 1. Gemini Tool 테스트
**파일**: `tests/integration/test_gemini_tool.py`

```python
import pytest
from src.tools.gemini_tool import GeminiTool
from src.clients.gemini_client import GeminiClient

@pytest.mark.integration
class TestGeminiToolIntegration:
    @pytest.fixture
    async def setup(self):
        api_key = os.getenv("GEMINI_API_KEY")
        client = GeminiClient(api_key)
        return client

    @pytest.mark.asyncio
    async def test_generate_code_tool(self, setup):
        """Gemini Tool 전체 흐름 테스트"""
        client = setup
        arguments = {
            "prompt": "Python으로 피보나치 함수 만들기",
            "language": "python"
        }

        result = await GeminiTool.execute(client, arguments)

        assert "code" in result
        assert "fibonacci" in result["code"].lower()
        assert result["language"] == "python"
```

### 2. Drive Tool 테스트
**파일**: `tests/integration/test_drive_tool.py`

```python
import pytest
from src.tools.drive_tool import DriveTool
from src.clients.drive_client import DriveClient

@pytest.mark.integration
class TestDriveToolIntegration:
    @pytest.fixture
    async def setup(self):
        creds_path = "config/credentials.json"
        client = DriveClient(creds_path)
        return client

    @pytest.mark.asyncio
    async def test_save_and_read_workflow(self, setup):
        """파일 저장 및 읽기 워크플로우"""
        client = setup

        # 1. 파일 저장
        save_args = {
            "content": "def test():\n    pass",
            "filename": "test_integration.py"
        }
        save_result = await DriveTool.save_file(client, save_args)

        assert "file_id" in save_result
        file_id = save_result["file_id"]

        # 2. 파일 읽기
        read_args = {"file_id": file_id}
        read_result = await DriveTool.read_file(client, read_args)

        assert read_result == "def test():\n    pass"

        # 3. 정리: 파일 삭제
        await client.delete_file(file_id)
```

### 3. MCP Server 테스트
**파일**: `tests/integration/test_mcp_server.py`

```python
import pytest
import json
from src.mcp_server import GeminiDriveMCPServer

@pytest.mark.integration
class TestMCPServer:
    @pytest.fixture
    async def server(self):
        server = GeminiDriveMCPServer()
        await server.initialize()
        return server

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Tool 목록 조회 테스트"""
        tools = await server.handle_list_tools()

        tool_names = [t["name"] for t in tools]
        assert "generate_code" in tool_names
        assert "save_to_drive" in tool_names
        assert "read_from_drive" in tool_names

    @pytest.mark.asyncio
    async def test_call_generate_code_tool(self, server):
        """generate_code Tool 호출 테스트"""
        result = await server.handle_call_tool(
            tool_name="generate_code",
            arguments={
                "prompt": "print hello world in python"
            }
        )

        assert "content" in result
        assert len(result["content"]) > 0
```

## E2E 테스트

### Claude Desktop 통합 테스트
**파일**: `tests/e2e/test_claude_integration.py`

```python
import pytest
import subprocess
import json

@pytest.mark.e2e
class TestClaudeIntegration:
    """Claude Desktop과의 실제 연동 테스트"""

    def test_mcp_server_startup(self):
        """MCP 서버 시작 테스트"""
        proc = subprocess.Popen(
            ["python", "src/mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 초기화 메시지 확인
        output = proc.stdout.readline()
        assert output is not None

        proc.terminate()

    def test_tool_call_via_stdio(self):
        """stdio를 통한 Tool 호출 테스트"""
        proc = subprocess.Popen(
            ["python", "src/mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # JSON-RPC 요청 전송
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "generate_code",
                "arguments": {
                    "prompt": "python hello world"
                }
            },
            "id": 1
        }

        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()

        # 응답 읽기
        response_line = proc.stdout.readline()
        response = json.loads(response_line)

        assert response["id"] == 1
        assert "result" in response

        proc.terminate()
```

## 테스트 실행

### pytest 설정
**파일**: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Tests that take a long time

asyncio_mode = auto
```

### 실행 명령어

```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/unit -v

# 통합 테스트만
pytest tests/integration -v -m integration

# E2E 테스트만
pytest tests/e2e -v -m e2e

# 특정 파일
pytest tests/unit/test_gemini_client.py -v

# 커버리지 포함
pytest --cov=src --cov-report=html
```

## CI/CD 통합

### GitHub Actions
**파일**: `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run unit tests
        run: pytest tests/unit -v
      - name: Run integration tests
        run: pytest tests/integration -v
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## 테스트 체크리스트

### Phase 1: 단위 테스트
- [ ] Gemini Client 테스트 작성 및 통과
- [ ] Drive Client 테스트 작성 및 통과
- [ ] Context Manager 테스트 작성 및 통과
- [ ] Utils 테스트 작성 및 통과

### Phase 2: 통합 테스트
- [ ] Gemini Tool 테스트 작성 및 통과
- [ ] Drive Tool 테스트 작성 및 통과
- [ ] Context Tool 테스트 작성 및 통과
- [ ] MCP Server 테스트 작성 및 통과

### Phase 3: E2E 테스트
- [ ] MCP Server stdio 통신 테스트
- [ ] Claude Desktop 연동 테스트
- [ ] 전체 워크플로우 테스트

### Phase 4: 성능 및 안정성
- [ ] API Rate Limiting 테스트
- [ ] 에러 복구 테스트
- [ ] 장시간 실행 안정성 테스트

## 테스트 커버리지 목표

- **단위 테스트**: 80% 이상
- **통합 테스트**: 주요 워크플로우 100%
- **E2E 테스트**: 핵심 시나리오 100%

---

**마지막 업데이트**: 2025-11-07
**다음 단계**: 테스트 코드 작성 시작
