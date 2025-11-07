"""Gemini API 클라이언트"""
import re
import base64
import google.generativeai as genai
from typing import Optional, Dict
from PIL import Image
import io


class GeminiClient:
    """Gemini API 클라이언트 클래스"""

    def __init__(self, api_key: str):
        """
        Gemini 클라이언트 초기화

        Args:
            api_key: Gemini API 키

        Raises:
            ValueError: API 키가 제공되지 않은 경우
        """
        if not api_key:
            raise ValueError("Gemini API 키가 필요합니다.")

        self.api_key = api_key
        self.conversation_history = []

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            raise RuntimeError(f"Gemini API 설정 실패: {str(e)}")

    async def generate_code(
        self,
        prompt: str,
        language: Optional[str] = None,
        context: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Dict[str, str]:
        """
        코드 생성 (비동기)

        Args:
            prompt: 코드 생성 요청 프롬프트
            language: 프로그래밍 언어 (선택)
            context: 이전 컨텍스트 (선택)

        Returns:
            {
                "code": "생성된 코드",
                "language": "감지된 언어",
                "explanation": "코드 설명"
            }

        Raises:
            Exception: 코드 생성 실패 시
        """
        try:
            full_prompt = self._build_prompt(prompt, language, context)

            # 이미지가 있으면 멀티모달 입력으로 처리
            if image_base64:
                # Base64 디코딩
                image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
                image = Image.open(io.BytesIO(image_data))

                # 이미지와 텍스트를 함께 전달
                response = self.model.generate_content([full_prompt, image])
            else:
                # 텍스트만 전달
                response = self.model.generate_content(full_prompt)

            code = self._extract_code(response.text)
            detected_language = language or self._detect_language(response.text)
            explanation = self._extract_explanation(response.text, code)

            # 대화 이력 저장
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": code
            })

            return {
                "code": code,
                "language": detected_language,
                "explanation": explanation
            }
        except Exception as e:
            raise Exception(f"코드 생성 실패: {str(e)}")

    def _build_prompt(
        self,
        user_request: str,
        language: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """프롬프트 구성"""
        system_prompt = """당신은 실행 가능한 완전한 애플리케이션을 생성하는 AI입니다.

**중요 규칙:**
1. 사용자가 "웹", "앱", "프로그램", "사이트" 등을 요청하면 **반드시 Streamlit 또는 Flask 웹 애플리케이션**으로 만들어야 합니다
2. requirements.txt에 필요한 모든 라이브러리를 명시하세요
3. README.md에 실행 방법을 상세히 작성하세요
4. 코드는 바로 실행 가능해야 합니다 (복사/붙여넣기 필요 없이)
5. 한글 주석으로 설명을 달아주세요

**웹앱 생성 시:**
- Streamlit 사용 (간단한 경우)
- Flask 사용 (복잡한 경우)
- 파일 업로드, 입력 폼 등 UI 포함
- 결과를 웹에서 바로 확인 가능하도록 구현

**출력 형식:**
```python
# main.py 또는 app.py
코드 내용
```

```
# requirements.txt
필요한 라이브러리
```

```markdown
# README.md
실행 방법
```
3. 코드 블록(```) 사용
4. 실행 가능하고 완전한 코드 작성
"""

        parts = [system_prompt]

        if language:
            parts.append(f"\n프로그래밍 언어: {language}")

        if context:
            parts.append(f"\n컨텍스트:\n{context}")

        parts.append(f"\n사용자 요청:\n{user_request}")

        return "\n".join(parts)

    def _extract_code(self, response_text: str) -> str:
        """코드 블록 추출"""
        # 코드 블록 찾기
        if "```" in response_text:
            start = response_text.find("```")
            end = response_text.find("```", start + 3)

            if start != -1 and end != -1:
                code_block = response_text[start + 3:end].strip()

                # 첫 줄이 언어 이름인 경우 제거
                if "\n" in code_block:
                    first_line = code_block.split("\n")[0].strip()
                    if first_line.lower() in [
                        "python", "javascript", "java", "cpp", "c",
                        "go", "rust", "typescript", "ruby", "php"
                    ]:
                        code_block = "\n".join(code_block.split("\n")[1:])

                return code_block

        # 코드 블록이 없으면 전체 텍스트 반환
        return response_text.strip()

    def _detect_language(self, response_text: str) -> str:
        """언어 감지"""
        # 코드 블록에서 언어 정보 추출
        match = re.search(r"```(\w+)", response_text)
        if match:
            return match.group(1).lower()

        # 기본값
        return "text"

    def _extract_explanation(self, response_text: str, code: str) -> str:
        """코드 설명 추출"""
        # 코드 블록 전후의 텍스트를 설명으로 간주
        explanation_parts = response_text.replace(f"```{code}```", "").strip()

        # 불필요한 문구 제거
        explanation_parts = re.sub(r"```\w*\n", "", explanation_parts)
        explanation_parts = re.sub(r"```", "", explanation_parts)

        return explanation_parts.strip() if explanation_parts else "코드가 생성되었습니다."

    def get_conversation_history(self) -> list:
        """대화 이력 반환"""
        return self.conversation_history

    def clear_history(self):
        """대화 이력 초기화"""
        self.conversation_history = []
