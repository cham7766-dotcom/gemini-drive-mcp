"""Gemini API 클라이언트"""
import google.generativeai as genai
from utils import print_error, print_info, print_success

class GeminiClient:
    """Gemini API 클라이언트 클래스"""
    
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API 키가 필요합니다.")
        
        self.api_key = api_key
        self.conversation_history = []
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print_success("Gemini API 연결 성공!")
        except Exception as e:
            print_error(f"Gemini API 설정 실패: {str(e)}")
            raise
    
    def generate_code(self, prompt, context=None):
        """코드 생성"""
        try:
            print_info("Gemini AI에 코드 생성 요청 중...")
            
            full_prompt = self._build_prompt(prompt, context)
            response = self.model.generate_content(full_prompt)
            generated_code = self._extract_code(response.text)
            
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": generated_code
            })
            
            print_success("코드 생성 완료!")
            return generated_code
        except Exception as e:
            print_error(f"코드 생성 실패: {str(e)}")
            raise
    
    def _build_prompt(self, user_request, context=None):
        """프롬프트 구성"""
        system_prompt = """당신은 코드 생성 전문 AI입니다.
규칙:
1. 코드에 상세한 주석 포함
2. 코드만 생성
3. 코드 블록(```) 사용
"""
        if context:
            return f"{system_prompt}\n\n컨텍스트:\n{context}\n\n사용자 요청:\n{user_request}"
        return f"{system_prompt}\n\n사용자 요청:\n{user_request}"
    
    def _extract_code(self, response_text):
        """코드 추출"""
        if "```" in response_text:
            start = response_text.find("```")
            end = response_text.find("```", start + 3)
            if start != -1 and end != -1:
                code_block = response_text[start + 3:end].strip()
                if "\n" in code_block:
                    first_line = code_block.split("\n")[0]
                    if first_line.lower() in ["python", "javascript", "java"]:
                        code_block = "\n".join(code_block.split("\n")[1:])
                return code_block
        return response_text
