# API 설정 가이드 🔑

## 1. Gemini API 키 발급
1. https://aistudio.google.com/app/apikey 방문
2. API 키 생성
3. 키 복사

## 2. 환경 변수 설정
```bash
# config/.env 파일 생성
cp config/.env.example config/.env

# .env 파일 편집
GEMINI_API_KEY=여기에_발급받은_키_입력
```

## 3. 테스트
```bash
python src/main.py
```

완료! 이제 사용할 수 있습니다.
