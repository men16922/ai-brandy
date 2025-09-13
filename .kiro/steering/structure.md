# 프로젝트 구조 및 아키텍처 패턴

## 디렉토리 구조

```
ai-branding-chatbot/
├── app.py                 # Streamlit 메인 애플리케이션 진입점
├── config/               # 애플리케이션 설정
│   ├── app_config.py     # 환경별 설정 관리
│   └── langchain_config.py # LangChain 초기화
├── core/                 # 핵심 비즈니스 로직
├── adapters/             # AI 모델 어댑터 (OpenAI, Gemini, Bedrock)
├── chains/               # LangChain 체인 구현
├── rag/                  # RAG (검색 증강 생성) 구현
├── storage/              # 데이터 저장소 추상화
│   ├── base_storage.py   # 저장소 기본 인터페이스
│   ├── unified_storage.py # 통합 저장소 구현
│   ├── storage_factory.py # 저장소 팩토리
│   └── data_initializer.py # 초기 데이터 로드
├── models/               # 데이터 모델 정의
│   └── data_models.py    # Pydantic/Dataclass 모델
├── utils/                # 유틸리티 함수
│   ├── logger.py         # 구조화된 로깅 시스템
│   └── models.py         # 공통 모델 유틸리티
├── data/                 # 정적 데이터 및 초기화 파일
│   ├── business_types.json # 업종 데이터
│   └── regions.json      # 지역 데이터
├── tests/                # 테스트 및 검증 스크립트
├── logs/                 # 로그 파일 저장소
├── reports/              # 생성된 PDF 보고서
└── docker/               # Docker 볼륨 데이터
    ├── dynamodb/         # DynamoDB Local 데이터
    ├── minio/            # MinIO 데이터
    └── chroma/           # Chroma DB 데이터
```

## 아키텍처 패턴

### 1. 환경별 설정 패턴
- **Factory Pattern**: `StorageFactory`로 환경별 저장소 생성
- **Singleton Pattern**: `AppConfig`로 전역 설정 관리
- **Strategy Pattern**: Local(MinIO+DynamoDB Local) vs Dev(S3+DynamoDB) 자동 선택

### 2. 데이터 모델 패턴
- **Dataclass**: 타입 안전성과 직렬화 지원
- **DynamoDB Single Table Design**: PK/SK 패턴 사용
- **환경별 테이블명**: `brandy-{table}-{environment}` 형식

### 3. 로깅 패턴
- **구조화된 로깅**: JSON 형태로 로그 출력
- **컨텍스트 매니저**: `LoggedOperation`으로 성능 측정
- **이벤트 기반 로깅**: API 호출, 워크플로 단계, 이미지 생성 등

### 4. 저장소 추상화 패턴
- **Repository Pattern**: `BaseStorage` 인터페이스
- **Adapter Pattern**: AWS 서비스와 로컬 서비스 통합
- **환경 투명성**: 코드 변경 없이 환경 전환

## 코딩 컨벤션

### 파일명 규칙
- **Python 파일**: `snake_case.py`
- **클래스명**: `PascalCase`
- **함수/변수명**: `snake_case`
- **상수명**: `UPPER_SNAKE_CASE`

### 모듈 구조
- **`__init__.py`**: 각 패키지에 필수 포함
- **타입 힌트**: 모든 함수에 타입 힌트 사용
- **Docstring**: Google 스타일 docstring 사용

### 환경 변수 패턴
```python
# 환경별 설정 로드
environment = os.getenv("APP_ENV", "local")
config = get_app_config(environment)

# 조건부 로직
if config.is_local:
    # Local 환경 로직
else:
    # Dev 환경 로직
```

### DynamoDB 키 패턴
```python
# 단일 테이블 설계
PK = f"ENTITY_TYPE#{entity_id}"
SK = f"METADATA" or f"DETAIL#{detail_id}"

# GSI 패턴
GSI1PK = f"STATUS#{status}"
GSI1SK = f"{created_at}"
```

### 로깅 패턴
```python
# 구조화된 로깅
logger = get_logger(__name__)
logger.info("Operation completed", 
           session_id=session_id, 
           duration=duration)

# 성능 로깅
with LoggedOperation(logger, "image_generation"):
    result = generate_image(prompt)
```

## 의존성 관리

### 계층 구조
1. **app.py** → config, core
2. **core** → adapters, chains, storage, models
3. **storage** → models, utils
4. **utils** → (최하위 레이어)

### 순환 의존성 방지
- **인터페이스 사용**: `BaseStorage` 추상 클래스
- **의존성 주입**: Factory 패턴으로 구현체 주입
- **이벤트 기반**: 직접 참조 대신 이벤트/콜백 사용

## 테스트 전략

### 테스트 파일 위치
- **단위 테스트**: `tests/test_*.py`
- **통합 테스트**: `tests/integration/`
- **검증 스크립트**: `tests/verify_*.py`

### 환경별 테스트
```python
# 환경별 테스트 설정
@pytest.fixture
def storage_client():
    return StorageFactory.create_storage("local")
```