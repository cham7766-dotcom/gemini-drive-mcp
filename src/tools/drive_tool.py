"""Google Drive 파일 관리 Tool"""
from typing import Dict, Any, Optional
from src.clients.drive_client import DriveClient


class DriveTool:
    """Google Drive 파일 관리 MCP Tools"""

    @staticmethod
    def get_save_definition() -> Dict[str, Any]:
        """파일 저장 Tool 정의"""
        return {
            "name": "save_to_drive",
            "description": "Google Drive에 파일을 저장합니다. 생성된 코드나 텍스트를 Drive에 업로드합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "저장할 파일 내용"
                    },
                    "filename": {
                        "type": "string",
                        "description": "파일 이름 (확장자 포함). 예: script.py, app.js"
                    },
                    "folder": {
                        "type": "string",
                        "description": "저장할 폴더 이름 (선택). 없으면 기본 폴더에 저장"
                    }
                },
                "required": ["content", "filename"]
            }
        }

    @staticmethod
    def get_read_definition() -> Dict[str, Any]:
        """파일 읽기 Tool 정의"""
        return {
            "name": "read_from_drive",
            "description": "Google Drive에서 파일을 읽어옵니다. 파일 ID 또는 파일 이름으로 검색하여 내용을 가져옵니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "파일 ID (file_id와 filename 중 하나 필수)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "파일 이름 (file_id와 filename 중 하나 필수)"
                    },
                    "folder": {
                        "type": "string",
                        "description": "검색할 폴더 이름 (선택)"
                    }
                }
            }
        }

    @staticmethod
    def get_list_definition() -> Dict[str, Any]:
        """파일 목록 조회 Tool 정의"""
        return {
            "name": "list_drive_files",
            "description": "Google Drive의 파일 목록을 조회합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "조회할 폴더 이름 (선택). 없으면 전체 파일 조회"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "최대 결과 수 (기본: 20)",
                        "default": 20
                    }
                }
            }
        }

    @staticmethod
    async def save_file(
        drive_client: DriveClient,
        context_manager: Any,
        arguments: Dict[str, Any],
        default_folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        파일 저장 실행

        Args:
            drive_client: Drive API 클라이언트
            context_manager: 컨텍스트 매니저
            arguments: Tool 인자
            default_folder: 기본 폴더 이름

        Returns:
            Dict: 저장 결과
        """
        content = arguments.get("content")
        filename = arguments.get("filename")
        folder_name = arguments.get("folder") or default_folder

        if not content:
            raise ValueError("'content' 인자가 필요합니다.")
        if not filename:
            raise ValueError("'filename' 인자가 필요합니다.")

        # 폴더 ID 가져오기 또는 생성
        folder_id = None
        if folder_name:
            folder_id = await drive_client.create_folder(folder_name)

        # 파일 업로드
        result = await drive_client.upload_file(
            content=content,
            filename=filename,
            folder_id=folder_id
        )

        # 컨텍스트에 저장
        context_manager.add_interaction(
            user_message=f"파일 저장: {filename}",
            assistant_response=f"Drive에 저장 완료: {result['web_view_link']}",
            metadata={
                "tool": "save_to_drive",
                "file_id": result["file_id"],
                "filename": filename,
                "folder": folder_name
            }
        )
        context_manager.save_session()

        return {
            "success": True,
            "file_id": result["file_id"],
            "filename": result["file_name"],
            "web_view_link": result["web_view_link"],
            "folder": folder_name,
            "message": f"파일이 Google Drive에 저장되었습니다: {result['web_view_link']}"
        }

    @staticmethod
    async def read_file(
        drive_client: DriveClient,
        context_manager: Any,
        arguments: Dict[str, Any],
        default_folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        파일 읽기 실행

        Args:
            drive_client: Drive API 클라이언트
            context_manager: 컨텍스트 매니저
            arguments: Tool 인자
            default_folder: 기본 폴더 이름

        Returns:
            Dict: 파일 내용
        """
        file_id = arguments.get("file_id")
        filename = arguments.get("filename")
        folder_name = arguments.get("folder") or default_folder

        if not file_id and not filename:
            raise ValueError("'file_id' 또는 'filename' 인자가 필요합니다.")

        # 파일 ID가 없으면 이름으로 검색
        if not file_id:
            folder_id = None
            if folder_name:
                folder_id = await drive_client.create_folder(folder_name)

            file_info = await drive_client.search_file(filename, folder_id)
            if not file_info:
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filename}")

            file_id = file_info["id"]
            filename = file_info["name"]

        # 파일 다운로드
        content = await drive_client.download_file(file_id)

        # 컨텍스트에 저장
        context_manager.add_interaction(
            user_message=f"파일 읽기: {filename}",
            assistant_response=f"파일 내용을 불러왔습니다 ({len(content)} 문자)",
            metadata={
                "tool": "read_from_drive",
                "file_id": file_id,
                "filename": filename
            }
        )
        context_manager.save_session()

        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "content": content,
            "size": len(content),
            "message": f"파일을 성공적으로 읽었습니다: {filename}"
        }

    @staticmethod
    async def list_files(
        drive_client: DriveClient,
        arguments: Dict[str, Any],
        default_folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        파일 목록 조회 실행

        Args:
            drive_client: Drive API 클라이언트
            arguments: Tool 인자
            default_folder: 기본 폴더 이름

        Returns:
            Dict: 파일 목록
        """
        folder_name = arguments.get("folder") or default_folder
        max_results = arguments.get("max_results", 20)

        folder_id = None
        if folder_name:
            folder_id = await drive_client.create_folder(folder_name)

        files = await drive_client.list_files(
            folder_id=folder_id,
            max_results=max_results
        )

        return {
            "success": True,
            "folder": folder_name,
            "count": len(files),
            "files": files,
            "message": f"{len(files)}개의 파일을 찾았습니다."
        }
