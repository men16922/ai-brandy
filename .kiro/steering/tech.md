# 기술 스택 및 빌드 시스템

## 핵심 기술 스택

### 웹 프레임워크
- **Streamlit 1.39.0**: 메인 웹 UI 프레임워크
- 5단계 워크플로 UI 구현

### AI/ML 프레임워크
- **LangChain 0.3.7**: AI 체인 오케스트레이션
  - `langchain-openai`: OpenAI/DALL-E 체인
  - `langchain-aws`: AWS Bedrock/SDXL 체인  
  - `langchain-google-genai`: Google Gemini 체인
  - `langchain-chroma`: Chroma 벡터 스토어

### 데이터베이스 및 저장소
- **DynamoDB**: 메인 데이터베이스 (Local: DynamoDB Local, Dev: AWS DynamoDB)
- **S3/MinIO**: 이미지 및 파일 저장소 (Local: MinIO, Dev: AWS S3)
- **Chroma DB**: 벡터 데이터베이스 (Local: Chroma, Dev: Bedrock Knowledge Base)

### AWS 서비스
- **boto3 1.35.63**: AWS SDK
- **DynamoDB**: NoSQL 데이터베이스
- **S3**: 객체 저장소
- **Bedrock**: AI 모델 서비스

### 개발 도구
- **Docker & Docker Compose**: 컨테이너화 및 로컬 개발 환경
- **Python 3.11+**: 메인 개발 언어
- **pytest**: 테스트 프레임워크

## 환경 설정

### Local 환경
```bash
# 환경 변수 로드
export $(cat .env.local | xargs)

# 백엔드 서비스 시작
docker-compose up -d

# 애플리케이션 실행
streamlit run app.py
```

### Dev 환경
```bash
# 환경 변수 로드
export $(cat .env.dev | xargs)

# 애플리케이션 실행
APP_ENV=dev streamlit run app.py
```

## 공통 명령어

### 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### Docker 관리
```bash
# 서비스 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f [service-name]

# 서비스 중지
docker-compose down

# 볼륨 포함 완전 삭제
docker-compose down -v
```

### 테스트 및 검증
```bash
# 프로젝트 설정 검증
python3 tests/verify_setup.py

# 기동 테스트
python3 tests/startup_test.py

# 저장소 시스템 테스트
python3 tests/test_storage_system.py
```

### 코드 품질
```bash
# 코드 포맷팅
black .

# 린팅
flake8 .

# 타입 체크 (향후 구현)
mypy .
```

## 포트 설정

- **8501**: Streamlit 애플리케이션
- **8000**: DynamoDB Local
- **8001**: DynamoDB Admin UI
- **9000**: MinIO API
- **9001**: MinIO Console
- **8003**: Chroma DB

## 환경 변수 패턴

- `.env.local`: 로컬 개발 환경
- `.env.dev`: AWS 개발 환경
- `APP_ENV`: 환경 구분자 (local/dev)
- `LOG_LEVEL`: 로그 레벨 (DEBUG/INFO)