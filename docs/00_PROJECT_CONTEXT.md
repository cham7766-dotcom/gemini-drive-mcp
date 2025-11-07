# 프로젝트 마스터 문서 📋

## 프로젝트 개요
**Gemini-Drive MCP**: Claude Desktop과 VS Code에서 Gemini AI를 활용하여 코드를 생성하고, Google Drive에 자동으로 저장/관리하는 MCP(Model Context Protocol) 서버

## 핵심 목표
1. **VS Code/Claude Desktop 통합**: MCP 프로토콜을 통한 원활한 연동
2. **Gemini AI 코드 생성**: 자연어 요청으로 코드 생성
3. **Google Drive 자동 저장**: 생성된 코드를 Drive에 자동 저장
4. **코드 수정 및 관리**: Gemini를 통한 기존 코드 수정 및 버전 관리

## 사용자 워크플로우
```
1. VS Code/Claude Desktop에서 요청
   ↓
2. MCP 서버가 Gemini API로 코드 생성
   ↓
3. 생성된 코드를 Google Drive에 자동 저장
   ↓
4. 저장된 파일 정보 반환
   ↓
5. 필요시 Gemini로 코드 수정 요청
```

## 주요 기능

### 1. MCP Tools (Claude Desktop에서 사용 가능한 도구)
- `generate_code`: Gemini로 코드 생성
- `save_to_drive`: Google Drive에 파일 저장
- `read_from_drive`: Drive에서 파일 읽기
- `update_code`: 기존 코드 수정
- `list_files`: Drive 파일 목록 조회
- `get_context`: 이전 작업 컨텍스트 조회

### 2. 컨텍스트 관리
- 대화 이력 저장 및 관리
- 세션별 작업 내역 추적
- 이전 작업 내용 기반 연속 작업 지원

### 3. Google Drive 연동
- OAuth 2.0 인증
- 파일 업로드/다운로드
- 폴더 구조 관리
- 파일 버전 관리

## 프로젝트 구조
```
gemini-drive-mcp/
├── docs/                      # 문서
│   ├── 00_PROJECT_CONTEXT.md  # 이 문서 (프로젝트 개요)
│   ├── 01_ARCHITECTURE.md     # MCP 서버 아키텍처
│   ├── 02_API_SETUP.md        # API 설정 가이드
│   ├── 03_IMPLEMENTATION.md   # 구현 계획
│   └── 04_TESTING.md          # 테스트 계획
│
├── src/
│   ├── mcp_server.py          # MCP 서버 메인
│   ├── tools/                 # MCP Tools
│   │   ├── __init__.py
│   │   ├── gemini_tool.py     # Gemini 코드 생성
│   │   ├── drive_tool.py      # Drive 파일 관리
│   │   └── context_tool.py    # 컨텍스트 관리
│   ├── clients/               # API 클라이언트
│   │   ├── __init__.py
│   │   ├── gemini_client.py   # Gemini API 클라이언트
│   │   └── drive_client.py    # Google Drive API 클라이언트
│   ├── managers/              # 관리자 클래스
│   │   ├── __init__.py
│   │   ├── context_manager.py # 컨텍스트 관리
│   │   └── session_manager.py # 세션 관리
│   └── utils/                 # 유틸리티
│       ├── __init__.py
│       ├── config.py          # 설정 로드
│       └── logger.py          # 로깅
│
├── tests/                     # 테스트
│   ├── test_gemini_client.py
│   ├── test_drive_client.py
│   ├── test_mcp_tools.py
│   └── test_integration.py
│
├── config/                    # 설정
│   ├── .env                   # 환경 변수 (API 키)
│   ├── .env.example           # 환경 변수 템플릿
│   └── credentials.json       # Google OAuth 인증
│
├── context/                   # 세션 데이터
│   └── session_*.json         # 세션별 대화 이력
│
├── logs/                      # 로그
│   └── mcp_server.log
│
├── claude_desktop_config.json # Claude Desktop 설정
├── requirements.txt           # Python 패키지
└── README.md                  # 프로젝트 README
```

## 기술 스택

### 핵심 기술
- **MCP (Model Context Protocol)**: Claude Desktop 연동
- **Python 3.8+**: 서버 구현 언어
- **Google Gemini API**: AI 코드 생성
- **Google Drive API**: 파일 저장 및 관리

### 주요 라이브러리
```python
# MCP 서버
mcp>=0.1.0

# AI & Google APIs
google-generativeai>=0.3.0     # Gemini API
google-api-python-client>=2.100.0  # Google Drive API
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0

# 유틸리티
python-dotenv>=1.0.0           # 환경 변수 관리
colorama>=0.4.6                # 터미널 색상
```

## 개발 단계

### Phase 1: 기반 구조 (현재)
- [x] 프로젝트 구조 설계
- [x] API 키 발급 (Gemini, Google Drive)
- [x] 기본 클라이언트 코드 작성
- [ ] MCP 서버 구조 설계
- [ ] 문서 작성 완료

### Phase 2: MCP 서버 구현
- [ ] MCP 서버 초기화
- [ ] Gemini 코드 생성 Tool 구현
- [ ] Google Drive Tool 구현
- [ ] 컨텍스트 관리 Tool 구현

### Phase 3: 테스트 및 검증
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] Claude Desktop 연동 테스트

### Phase 4: 최적화 및 배포
- [ ] 성능 최적화
- [ ] 에러 처리 강화
- [ ] 사용자 문서 작성

## 주요 제약사항
1. **MCP 프로토콜 준수**: Claude Desktop과 호환되어야 함
2. **API 제한**: Gemini API 및 Drive API의 할당량 관리
3. **인증 보안**: API 키 및 OAuth 토큰의 안전한 관리
4. **동기화**: Drive 파일과 로컬 세션의 일관성 유지

## 성공 기준
1. ✅ Claude Desktop에서 MCP 서버 인식
2. ✅ Gemini로 코드 생성 성공
3. ✅ Google Drive에 파일 저장 성공
4. ✅ 저장된 파일 읽기 및 수정 성공
5. ✅ 컨텍스트 기반 연속 작업 가능

## 참고 문서
- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Google Drive API 문서](https://developers.google.com/drive)
- [Claude Desktop 문서](https://claude.ai/desktop)

---

**마지막 업데이트**: 2025-11-07
**버전**: v2.0 (MCP 서버 재설계)
