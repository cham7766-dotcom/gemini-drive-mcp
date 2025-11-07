# 설치 가이드 📦

## 필수 요구사항
- Python 3.8 이상
- 인터넷 연결
- Google 계정

## Step 1: 가상 환경 설정

### Windows
```bash
cd C:\Users\chosun\Desktop\gemini-drive-mcp
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux
```bash
cd ~/Desktop/gemini-drive-mcp
python3 -m venv venv
source venv/bin/activate
```

## Step 2: 패키지 설치
```bash
pip install -r requirements.txt
```

## Step 3: 설치 확인
```bash
python tests/test_installation.py
```

## 다음 단계
- API 설정: 02_API_SETUP.md 참조
- 사용법: 03_USAGE_GUIDE.md 참조
