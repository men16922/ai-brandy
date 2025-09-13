# AI 브랜딩 챗봇

AI를 활용한 브랜딩 솔루션으로 상호명 추천부터 간판/인테리어 디자인까지 제공하는 통합 서비스입니다.

## 주요 기능

- **상호명 추천**: 업종과 지역에 맞는 상호명 3개 추천
- **간판 디자인**: DALL-E 3, SDXL, Gemini를 활용한 간판 이미지 생성
- **인테리어 추천**: 선택한 간판과 조화를 맞춘 인테리어 디자인
- **PDF 보고서**: 모든 선택사항을 포함한 완성된 보고서 생성
- **환경별 실행**: Local(Docker) 및 Dev(AWS) 환경 지원

## 시스템 요구사항

- Python 3.11+
- Docker & Docker Compose
- 8GB+ RAM 권장

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone <repository-url>
cd ai-branding-chatbot

# 2. 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 백엔드 서비스 시작
docker-compose up -d dynamodb-local chroma-db

# 4. 애플리케이션 실행
export $(cat .env.local | xargs)
streamlit run app.py

# 5. 브라우저에서 접속
# http://localhost:8501
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd ai-branding-chatbot

# API 키가 .env.local에 이미 설정되어 있습니다
# 필요시 .env.local 파일에서 수정 가능
```

### 2. 로컬 개발 환경 실행 (권장)

#### 2-1. Python 가상환경 설정
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

#### 2-2. 백엔드 서비스 시작
```bash
# DynamoDB Local과 Chroma DB만 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
```

#### 2-3. 애플리케이션 실행
```bash
# 환경 변수 로드 및 앱 실행
export $(cat .env.local | xargs)
streamlit run app.py

# 또는 직접 실행
APP_ENV=local streamlit run app.py
```

#### 2-4. 접속 확인
- **메인 애플리케이션**: http://localhost:8501
- **헬스체크**: http://localhost:8501/?health=true
- **DynamoDB Local**: http://localhost:8000
- **Chroma DB**: http://localhost:8001

### 3. Docker로 전체 스택 실행

```bash
# 모든 서비스 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f ai-branding-app

# 애플리케이션 접속
open http://localhost:8501

# 서비스 중지
docker-compose down
```

## 환경별 설정

### Local 환경 (.env.local)
- DynamoDB Local (포트 8000)
- Chroma Vector DB (포트 8001)
- AWS S3 (실제 AWS 서비스 사용)

### Dev 환경 (.env.dev)
- AWS DynamoDB
- AWS S3
- Bedrock Knowledge Base

## 프로젝트 구조

```
ai-branding-chatbot/
├── app.py                 # Streamlit 메인 애플리케이션
├── config/               # 설정 파일
├── core/                 # 핵심 비즈니스 로직
├── adapters/             # AI 모델 어댑터
├── storage/              # 데이터 저장소
├── utils/                # 유틸리티
├── data/                 # 초기 데이터
├── logs/                 # 로그 파일
├── reports/              # 생성된 보고서
├── tests/                # 테스트 및 검증 스크립트
└── docker/               # Docker 설정 및 볼륨 데이터
    ├── compose/          # Docker Compose 파일들
    ├── chroma/           # Chroma DB 데이터
    └── dynamodb/         # DynamoDB Local 데이터
```

## API 키 설정

다음 API 키들이 필요합니다:

- `OPENAI_API_KEY`: OpenAI API (DALL-E 3, GPT)
- `GOOGLE_API_KEY`: Google Gemini API
- `ANTHROPIC_API_KEY`: Anthropic Claude API (선택사항)

## 개발 가이드

### 코드 스타일
```bash
# 코드 포맷팅
black .

# 린팅
flake8 .
```

### 테스트
```bash
# 프로젝트 설정 검증
python3 tests/verify_setup.py

# 기동 테스트
python3 tests/startup_test.py

# 단위 테스트 (향후 구현)
pytest tests/

# 통합 테스트 (향후 구현)
pytest tests/integration/
```

## 문제 해결

### 포트 충돌 해결
```bash
# 사용 중인 포트 확인
lsof -i :8501  # Streamlit
lsof -i :8000  # DynamoDB Local
lsof -i :8001  # Chroma DB

# 프로세스 종료
kill -9 <PID>
```

### Docker 관련
```bash
# 서비스 재시작
docker-compose down
docker-compose up -d dynamodb-local chroma-db

# 볼륨 권한 문제
sudo chown -R $USER:$USER docker/

# 이미지 재빌드
docker-compose build --no-cache
```

### Python 환경 관련
```bash
# 가상환경 재생성
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 환경 변수 확인
echo $APP_ENV
echo $OPENAI_API_KEY

# Streamlit 버전 확인
python3 -c "import streamlit as st; print(f'Streamlit: {st.__version__}')"
```

### Streamlit 관련 오류
```bash
# query_params 오류 해결 (버전 호환성)
# - 앱에서 헬스체크는 사이드바 버튼으로 대체됨
# - Streamlit 1.28+ 권장

# 의존성 재설치
source .venv/bin/activate
pip install --upgrade streamlit pydantic pydantic-settings
```

### API 관련
- **API 키 확인**: `.env.local` 파일의 키 값 검증
- **할당량 초과**: API 사용량 확인
- **네트워크 오류**: 방화벽 및 프록시 설정 확인

### 개발 팁
```bash
# 실시간 로그 확인
docker-compose logs -f dynamodb-local
docker-compose logs -f chroma-db

# 개발 중 자동 재시작
streamlit run app.py --server.runOnSave=true

# 디버그 모드 활성화
export LOG_LEVEL=DEBUG
export DEBUG_MODE=true
```

## 라이선스

MIT License