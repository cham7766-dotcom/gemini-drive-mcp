"""Google Drive API 클라이언트"""
import io
import os
from pathlib import Path
from typing import Optional, Dict, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# Drive API 권한 범위
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveClient:
    """Google Drive API 클라이언트"""

    def __init__(self, credentials_path: str, token_path: Optional[str] = None):
        """
        Drive 클라이언트 초기화

        Args:
            credentials_path: OAuth 인증 정보 파일 경로 (credentials.json)
            token_path: 토큰 저장 파일 경로 (token.json, None이면 자동 생성)

        Raises:
            FileNotFoundError: credentials 파일이 없는 경우
            Exception: 인증 실패 시
        """
        creds_file = Path(credentials_path)
        if not creds_file.exists():
            raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {credentials_path}")

        if token_path is None:
            token_path = creds_file.parent / "token.json"

        self.credentials_path = creds_file
        self.token_path = Path(token_path)
        self.creds = None
        self.service = None

        self._authenticate()

    def _authenticate(self):
        """OAuth 인증 처리"""
        # 기존 토큰 로드
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # 토큰이 없거나 유효하지 않으면 새로 발급
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # 토큰 갱신
                self.creds.refresh(Request())
            else:
                # 새로운 OAuth 플로우 시작
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(self.token_path, 'w') as token_file:
                token_file.write(self.creds.to_json())

        # Drive API 서비스 초기화
        self.service = build('drive', 'v3', credentials=self.creds)

    async def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """
        폴더 생성 (이미 존재하면 기존 폴더 ID 반환)

        Args:
            folder_name: 생성할 폴더 이름
            parent_id: 부모 폴더 ID (None이면 루트)

        Returns:
            str: 폴더 ID

        Raises:
            Exception: 폴더 생성 실패 시
        """
        try:
            # 기존 폴더 검색
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])

            if files:
                # 기존 폴더 반환
                return files[0]['id']

            # 새 폴더 생성
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except Exception as e:
            raise Exception(f"폴더 생성 실패: {str(e)}")

    async def upload_file(
        self,
        content: str,
        filename: str,
        folder_id: Optional[str] = None,
        mime_type: str = "text/plain"
    ) -> Dict[str, str]:
        """
        파일 업로드

        Args:
            content: 파일 내용 (문자열)
            filename: 파일 이름
            folder_id: 업로드할 폴더 ID (None이면 루트)
            mime_type: MIME 타입

        Returns:
            {
                "file_id": "파일 ID",
                "file_name": "파일 이름",
                "web_view_link": "웹 링크"
            }

        Raises:
            Exception: 업로드 실패 시
        """
        try:
            # 임시 파일 생성
            temp_file = Path(f"/tmp/{filename}")
            temp_file.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 메타데이터 구성
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # 파일 업로드
            media = MediaFileUpload(str(temp_file), mimetype=mime_type)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            # 임시 파일 삭제
            temp_file.unlink()

            return {
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "web_view_link": file.get('webViewLink')
            }

        except Exception as e:
            raise Exception(f"파일 업로드 실패: {str(e)}")

    async def download_file(self, file_id: str) -> str:
        """
        파일 다운로드

        Args:
            file_id: 다운로드할 파일 ID

        Returns:
            str: 파일 내용 (문자열)

        Raises:
            Exception: 다운로드 실패 시
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            file_io.seek(0)
            content = file_io.read().decode('utf-8')

            return content

        except Exception as e:
            raise Exception(f"파일 다운로드 실패: {str(e)}")

    async def search_file(self, filename: str, folder_id: Optional[str] = None) -> Optional[Dict]:
        """
        파일 이름으로 검색

        Args:
            filename: 검색할 파일 이름
            folder_id: 검색할 폴더 ID (None이면 전체)

        Returns:
            Dict: 파일 정보 (없으면 None)
            {
                "id": "파일 ID",
                "name": "파일 이름",
                "mimeType": "MIME 타입",
                "webViewLink": "웹 링크"
            }

        Raises:
            Exception: 검색 실패 시
        """
        try:
            query = f"name='{filename}' and trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink)',
                pageSize=1
            ).execute()

            files = results.get('files', [])

            if files:
                return files[0]

            return None

        except Exception as e:
            raise Exception(f"파일 검색 실패: {str(e)}")

    async def list_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        파일 목록 조회

        Args:
            folder_id: 조회할 폴더 ID (None이면 전체)
            query: 추가 검색 쿼리 (선택)
            max_results: 최대 결과 수

        Returns:
            List[Dict]: 파일 목록

        Raises:
            Exception: 조회 실패 시
        """
        try:
            base_query = "trashed=false"

            if folder_id:
                base_query += f" and '{folder_id}' in parents"

            if query:
                base_query += f" and {query}"

            results = self.service.files().list(
                q=base_query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, webViewLink)',
                pageSize=max_results,
                orderBy='createdTime desc'
            ).execute()

            return results.get('files', [])

        except Exception as e:
            raise Exception(f"파일 목록 조회 실패: {str(e)}")

    async def delete_file(self, file_id: str):
        """
        파일 삭제

        Args:
            file_id: 삭제할 파일 ID

        Raises:
            Exception: 삭제 실패 시
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
        except Exception as e:
            raise Exception(f"파일 삭제 실패: {str(e)}")

    def get_service(self):
        """Drive API 서비스 객체 반환"""
        return self.service
