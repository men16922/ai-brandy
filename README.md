# 🏪 AI 브랜딩 챗봇

AI를 활용한 브랜딩 솔루션으로 상호명 추천부터 간판/인테리어 디자인까지 제공하는 통합 서비스입니다.

## ✨ 주요 기능

### 5단계 워크플로
1. **비즈니스 정보 입력**: 업종, 지역, 평수 등 기본 정보 수집
2. **상호명 생성**: AI가 추천하는 3개의 상호명 (재생성 최대 3회)
3. **간판 디자인**: 선택된 상호명으로 3가지 간판 디자인 생성
4. **인테리어 추천**: 간판과 조화를 맞춘 3가지 인테리어 디자인
5. **PDF 보고서**: 최종 선택사항을 포함한 완성된 보고서 생성

### 기술 특징
- **멀티 AI 모델**: OpenAI DALL-E 3, AWS Bedrock SDXL, Google Gemini 지원
- **환경별 배포**: Local(Docker) 및 AWS Dev 환경 자동 전환
- **자동 초기화**: 테이블 생성 및 데이터 로드 자동화
- **헬스체크**: 실시간 시스템 상태 모니터링

## 🛠 시스템 요구사항

- **Python**: 3.11+
- **Docker**: Docker & Docker Compose
- **메모리**: 8GB+ RAM 권장
- **AWS CLI**: Dev 환경 사용 시 필요

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
docker-compose up -d

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

# local
streamlit run app.py

# dev
source venv/bin/activate
source .env.dev
streamlit run app.py

# 또는 직접 실행
APP_ENV=local streamlit run app.py
```

#### 2-4. 접속 확인
- **메인 애플리케이션**: http://localhost:8501
- **헬스체크**: http://localhost:8501/?health=true
- **DynamoDB Local**: http://localhost:8000
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **MinIO API**: http://localhost:9000
- **Chroma DB**: http://localhost:8003
- **DynamoDB Admin**: http://localhost:8002

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

```bash
## docker dynamodb TEST
aws dynamodb list-tables \
  --endpoint-url http://127.0.0.1:8000 \
  --region us-east-1 \
  --no-cli-pager --profile local-dynamodb

## dynamodb admin
http://localhost:8001

## minio
http://127.0.0.1:9001

## Chroma
http://127.0.0.1:8003/api/v2/version
```


### 4. CloudFormation으로 aws dev 환경 배포
```bash
aws sts get-caller-identity
./scripts/validate-template.sh
./scripts/deploy-infrastructure.sh -e dev

# yml 업데이트
./scripts/update-env-from-stack.sh

# 모든 리소스 삭제
./scripts/deploy-infrastructure.sh -e dev --delete

```

## 환경별 설정

### Local 환경 (.env.local)
- DynamoDB Local (포트 8000)
- MinIO (S3 호환 로컬 스토리지, 포트 9000/9001)
- Chroma Vector DB (포트 8003)

### Dev 환경 (.env.dev)
- AWS DynamoDB
- AWS S3
- Bedrock Knowledge Base

## 📁 프로젝트 구조

```
ai-branding-chatbot/
├── app.py                     # Streamlit 메인 애플리케이션
├── requirements.txt           # Python 의존성
├── docker-compose.yml         # Local 개발 환경
├── .env.local                 # Local 환경 설정
├── .env.dev                   # Dev 환경 설정
├── config/                    # 애플리케이션 설정
│   ├── app_config.py         # 환경별 설정 관리
│   └── langchain_config.py   # LangChain 초기화
├── storage/                   # 데이터 저장소 계층
│   ├── unified_storage.py    # 통합 저장소 구현
│   ├── storage_factory.py    # 저장소 팩토리
│   ├── data_initializer.py   # 데이터 초기화
│   ├── startup_initializer.py # 앱 시작 초기화
│   └── schemas/              # DynamoDB 스키마 정의
├── models/                    # 데이터 모델
│   └── data_models.py        # Pydantic/Dataclass 모델
├── utils/                     # 유틸리티 함수
│   ├── logger.py             # 구조화된 로깅
│   └── models.py             # 모델 유틸리티
├── data/                      # 정적 데이터
│   ├── regions.json          # 지역 데이터
│   └── business_types.json   # 업종 데이터
├── infrastructure/            # 인프라 코드 (IaC)
│   └── cloudformation/       # CloudFormation 템플릿
├── scripts/                   # 유틸리티 스크립트
│   ├── deploy-infrastructure.sh
│   └── validate-template.sh
├── tests/                     # 테스트 코드
├── docs/                      # 문서
├── logs/                      # 로그 파일 (런타임)
├── reports/                   # 생성된 보고서 (런타임)
└── docker/                    # Docker 볼륨 데이터 (런타임)
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
lsof -i :8003  # Chroma DB

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