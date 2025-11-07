"""Gemini-Drive MCP Server"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.clients.gemini_client import GeminiClient
from src.clients.drive_client import DriveClient
from src.managers.context_manager import ContextManager
from src.tools.gemini_tool import GeminiTool
from src.tools.drive_tool import DriveTool
from src.tools.context_tool import ContextTool
from src.utils.config import Config
from src.utils.logger import setup_logger


class GeminiDriveMCPServer:
    """Gemini-Drive MCP 서버"""

    def __init__(self):
        """MCP 서버 초기화"""
        # 설정 로드
        self.config = Config()

        # 로거 설정
        log_file = self.config.get_log_file()
        self.logger = setup_logger("GeminiDriveMCP", log_file, self.config.get_log_level())
        self.logger.info("MCP 서버 초기화 시작")

        # MCP Server 인스턴스
        self.server = Server("gemini-drive-mcp")

        # 클라이언트 초기화
        self.gemini_client = None
        self.drive_client = None
        self.context_manager = None

        # 기본 폴더 이름
        self.default_folder = self.config.get_drive_folder_name()

        self.logger.info("MCP 서버 초기화 완료")

    async def initialize_clients(self):
        """API 클라이언트 초기화"""
        try:
            # Gemini 클라이언트
            api_key = self.config.get_gemini_api_key()
            if not api_key:
                raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
            self.gemini_client = GeminiClient(api_key)
            self.logger.info("Gemini 클라이언트 초기화 완료")

            # Drive 클라이언트
            creds_path = self.config.get_credentials_path()
            token_path = self.config.get_token_path()
            self.drive_client = DriveClient(
                credentials_path=str(creds_path),
                token_path=str(token_path)
            )
            self.logger.info("Drive 클라이언트 초기화 완료")

            # Context Manager
            self.context_manager = ContextManager()
            self.logger.info(f"컨텍스트 매니저 초기화 완료 (세션: {self.context_manager.session_id})")

        except Exception as e:
            self.logger.error(f"클라이언트 초기화 실패: {e}")
            raise

    def register_tools(self):
        """MCP Tools 등록"""
        self.logger.info("MCP Tools 등록 시작")

        # Tools 목록 정의
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """사용 가능한 도구 목록 반환"""
            tools = [
                Tool(
                    name=GeminiTool.get_definition()["name"],
                    description=GeminiTool.get_definition()["description"],
                    inputSchema=GeminiTool.get_definition()["inputSchema"]
                ),
                Tool(
                    name=DriveTool.get_save_definition()["name"],
                    description=DriveTool.get_save_definition()["description"],
                    inputSchema=DriveTool.get_save_definition()["inputSchema"]
                ),
                Tool(
                    name=DriveTool.get_read_definition()["name"],
                    description=DriveTool.get_read_definition()["description"],
                    inputSchema=DriveTool.get_read_definition()["inputSchema"]
                ),
                Tool(
                    name=DriveTool.get_list_definition()["name"],
                    description=DriveTool.get_list_definition()["description"],
                    inputSchema=DriveTool.get_list_definition()["inputSchema"]
                ),
                Tool(
                    name=ContextTool.get_definition()["name"],
                    description=ContextTool.get_definition()["description"],
                    inputSchema=ContextTool.get_definition()["inputSchema"]
                ),
                Tool(
                    name=ContextTool.get_list_sessions_definition()["name"],
                    description=ContextTool.get_list_sessions_definition()["description"],
                    inputSchema=ContextTool.get_list_sessions_definition()["inputSchema"]
                )
            ]
            return tools

        # Tool 호출 핸들러
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Tool 실행"""
            self.logger.info(f"Tool 호출: {name}, 인자: {arguments}")

            try:
                result = None

                # Gemini 코드 생성
                if name == "generate_code":
                    result = await GeminiTool.execute(
                        self.gemini_client,
                        self.context_manager,
                        arguments
                    )

                # Drive 파일 저장
                elif name == "save_to_drive":
                    result = await DriveTool.save_file(
                        self.drive_client,
                        self.context_manager,
                        arguments,
                        self.default_folder
                    )

                # Drive 파일 읽기
                elif name == "read_from_drive":
                    result = await DriveTool.read_file(
                        self.drive_client,
                        self.context_manager,
                        arguments,
                        self.default_folder
                    )

                # Drive 파일 목록
                elif name == "list_drive_files":
                    result = await DriveTool.list_files(
                        self.drive_client,
                        arguments,
                        self.default_folder
                    )

                # 컨텍스트 조회
                elif name == "get_context":
                    result = await ContextTool.execute(
                        self.context_manager,
                        arguments
                    )

                # 세션 목록
                elif name == "list_sessions":
                    result = await ContextTool.list_sessions(
                        self.context_manager
                    )

                else:
                    raise ValueError(f"알 수 없는 도구: {name}")

                self.logger.info(f"Tool 실행 성공: {name}")

                # 결과를 문자열로 변환
                import json
                result_text = json.dumps(result, ensure_ascii=False, indent=2)

                return [TextContent(type="text", text=result_text)]

            except Exception as e:
                self.logger.error(f"Tool 실행 실패: {name}, 에러: {e}")
                error_message = f"오류 발생: {str(e)}"
                return [TextContent(type="text", text=error_message)]

        self.logger.info("MCP Tools 등록 완료")

    async def run(self):
        """MCP 서버 실행"""
        try:
            self.logger.info("MCP 서버 시작")

            # 클라이언트 초기화
            await self.initialize_clients()

            # Tools 등록
            self.register_tools()

            # stdio 서버 실행
            async with stdio_server() as (read_stream, write_stream):
                self.logger.info("stdio 서버 시작됨")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )

        except Exception as e:
            self.logger.error(f"서버 실행 중 오류: {e}")
            raise


async def main():
    """메인 진입점"""
    server = GeminiDriveMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n서버 종료")
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
