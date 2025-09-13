# 구현 계획 (LangChain 기반)

- [x] 1. 프로젝트 기본 구조 및 환경 설정
  - 프로젝트 디렉토리 구조 생성 (chains/, rag/, core/, storage/, utils/)
  - requirements.txt 작성 (LangChain 생태계 포함)
    - langchain, langchain-core, langchain-community
    - langchain-openai (OpenAI/DALL-E 체인)
    - langchain-aws (Bedrock/SDXL 체인)
    - langchain-google-genai (Gemini 체인)
    - langchain-chroma (Chroma 벡터 스토어)
    - Streamlit, boto3, chromadb, reportlab, plotly
  - .env 템플릿 파일 생성 (.env.local, .env.dev)
    - LangChain 관련 환경 변수 추가
    - LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY (선택사항)
    - LANGCHAIN_PROJECT (프로젝트 추적용)
  - LangChain 설정 파일 생성 (config/langchain_config.py)
    - 체인 기본 설정 및 콜백 핸들러
    - 환경별 LLM 모델 설정 (gpt-4o-mini vs gpt-4o)
    - 체인 캐싱 및 메모리 설정
  - Docker 환경 설정 (docker-compose.yml for local)
  - 기본 설정 파일 구조 생성 (config/, data/, logs/, reports/)
  - _요구사항: 5 환경별 실행_

- [x] 2. 로깅 시스템 구현
  - utils/logger.py 구조화된 로깅 클래스 작성
  - 환경별 로그 레벨 설정 (local: DEBUG, dev: INFO)
  - API 호출, 오류, 성능 메트릭 로깅 메서드 구현
  - 로그 파일 로테이션 및 보관 정책 구현
  - _요구사항: 6 로깅 & 안정성_

- [x] 3. 환경별 저장소 시스템 구현
  - storage/storage_factory.py 환경별 저장소 팩토리 클래스 작성
  - storage/local_storage.py DynamoDB Local + MinIO (S3 호환) 연동 구현
  - storage/aws_storage.py AWS DynamoDB + AWS S3 연동 구현
  - 데이터 모델 클래스들 작성 (models/data_models.py)
  - 헬스체크 기능 구현 (환경별 서비스 상태 확인)
  - _요구사항: 5 환경별 실행_

- [x] 3.1 JSON 데이터 DynamoDB 마이그레이션 시스템 구현
  - storage/data_initializer.py JSON → DynamoDB 마이그레이션 클래스 작성
  - DynamoDB 테이블 설계: brandy-regions-{env}, brandy-business-types-{env}
  - JSON 구조 변환 로직: 중첩 구조 → 평면 DynamoDB 아이템
  - 중복 방지 및 배치 삽입 로직 구현
  - 폴백 전략: DynamoDB 실패 시 JSON 파일 사용
  - _요구사항: 5 환경별 실행_

- [ ] 4. LangChain 기반 텍스트 생성 체인 구현
  - chains/text_chains.py LangChain 텍스트 생성 체인 구현
  - 상호명 생성 체인 (PromptTemplate + ChatOpenAI)
  - 분석 요약 생성 체인 (구조화된 출력)
  - 이미지 프롬프트 생성 체인 (간판/인테리어용)
  - 체인 파이프라인 및 오류 처리 구현
  - _요구사항: 1 상호명 추천_

- [ ] 5. LangChain 기반 이미지 생성 체인 구현
  - chains/image_chains.py LangChain 이미지 생성 체인 구현
  - DALL-E 3 체인 (langchain-openai 사용)
  - SDXL 체인 (langchain-aws Bedrock 사용)
  - Gemini 체인 (langchain-google-genai 사용)
  - 체인 병렬 실행 및 결과 집계 로직
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 6. LangChain RAG 시스템 구현 - 벡터 스토어
  - rag/vector_stores.py LangChain 벡터 스토어 구현
  - Chroma 벡터 스토어 (Local 환경, langchain-chroma)
  - Bedrock Knowledge Base 벡터 스토어 (Dev 환경, langchain-aws)
  - 문서 임베딩 및 검색 체인 구현
  - 벡터 스토어 팩토리 패턴 적용
  - _요구사항: 5 환경별 실행_

- [ ] 7. LangChain RAG 시스템 구현 - 검색 체인
  - rag/retrieval_chains.py LangChain 검색 체인 구현
  - RetrievalQA 체인으로 RAG 질의응답 구현
  - 다차원 분석용 검색 체인 (기존 사례 검색)
  - 상호명 위험도 검증 체인 (상표 검색)
  - 디자인 힌트 검색 체인 (트렌드 분석)
  - 표준화된 RAG 응답 스키마 적용
  - _요구사항: 전체 워크플로 RAG 지원_

- [ ] 8. 핵심 비즈니스 서비스 구현 (LangChain 통합)
  - core/business_service.py LangChain 체인 통합 비즈니스 로직
  - 텍스트 체인을 활용한 분석 및 상호명 생성
  - RAG 체인을 활용한 기존 사례 참조
  - 간단한 점수 계산 로직 (발음/검색 용이성)
  - 레이더 차트 데이터 생성 로직
  - _요구사항: 1 상호명 추천_

- [ ] 9. 이미지 생성 오케스트레이터 구현 (LangChain 통합)
  - core/image_orchestrator.py LangChain 이미지 체인 통합 관리
  - Base Image 검색 시스템과 LangChain 체인 연동
  - 간판 이미지 3안 생성 (DALL-E/SDXL/Gemini 체인 병렬 실행)
  - 인테리어 이미지 3안 생성 (선택된 간판과 조화)
  - 색상 팔레트 추출 및 예산 범위 계산
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 10. Base Image 검색 시스템 구현 (LangChain 통합)
  - core/base_image_search.py LangChain 임베딩 기반 이미지 검색
  - S3 이미지 메타데이터 벡터화 (LangChain Embeddings 사용)
  - 키워드 기반 검색 체인 구현
  - 지역별 이미지 필터링 및 유사도 검색
  - 폴백 이미지 제공 로직
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 11. PDF 보고서 생성 시스템 구현
  - core/pdf_generator.py PDF 보고서 생성 클래스
  - 보고서 템플릿 설계 (상호명, 이미지, 색상 팔레트, 예산, 분석 요약)
  - 이미지 썸네일 생성 및 레이아웃 구성
  - 선택 표시 기능 (선택된 간판/인테리어 하이라이트)
  - PDF 파일 저장 및 다운로드 링크 생성
  - _요구사항: 4 보고서 생성_

- [ ] 12. 워크플로 관리자 구현 (LangChain 통합)
  - core/workflow_manager.py 5단계 워크플로 상태 관리
  - DynamoDB 기반 세션 관리 (brandy-workflow 테이블)
  - LangChain 체인 실행 상태 추적 및 데이터 저장
  - 재생성 횟수 제한 관리 (상호명 최대 3회)
  - 진행률 계산 및 ETA 추정 로직
  - _요구사항: 전체 워크플로_

- [ ] 13. Streamlit UI 구현 - 1단계: 정보 입력
  - app.py 메인 애플리케이션 진입점 및 초기화
  - 1단계 UI: 업종/지역/평수 입력 폼
  - 사진 업로드 옵션 구현 (선택사항)
  - DynamoDB에서 지역/업종 데이터 로드 및 자동완성
  - 입력 검증 및 다음 단계 진행 버튼
  - _요구사항: 1 상호명 추천_

- [ ] 14. Streamlit UI 구현 - 2단계: 분석 요약
  - 2단계 UI: 분석 결과 표시
  - LangChain 체인으로 생성된 분석 결과 표시
  - 점수 표시 (발음/검색 용이성)
  - Plotly 레이더 차트 구현
  - RAG 검색 결과 기반 분석 요약 텍스트 표시
  - _요구사항: 1 상호명 추천_

- [ ] 15. Streamlit UI 구현 - 3단계: 상호명 제안
  - 3단계 UI: LangChain 체인으로 생성된 상호명 3개 표시
  - 각 상호명별 설명 및 점수 카드 형태 표시
  - RAG 기반 상호명 위험도 검증 결과 표시
  - 선택 버튼 및 재추천 버튼 (최대 3회)
  - 재추천 시 중복 회피 로직 연동
  - _요구사항: 1 상호명 추천_

- [ ] 16. Streamlit UI 구현 - 4단계: 이미지 생성
  - 4단계 UI: LangChain 이미지 체인으로 생성된 이미지 표시
  - 간판 3안 카드 형태 표시 (DALL-E/SDXL/Gemini 체인 결과)
  - 인테리어 3안 카드 형태 표시 (색상 팔레트 + 예산 포함)
  - Base Image 검색 결과 모드보드 표시
  - RAG 기반 디자인 힌트 표시
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 17. Streamlit UI 구현 - 5단계: 보고서 생성
  - 5단계 UI: PDF 보고서 생성 및 다운로드
  - LangChain 벡터 스토어에 보고서 저장
  - PDF 다운로드 버튼 구현
  - RAG 기반 보고서 교차검증 결과 표시
  - 벡터화 완료 상태 표시
  - _요구사항: 4 보고서 생성_

- [ ] 18. LangChain 체인 성능 최적화
  - 체인 실행 시간 모니터링 및 최적화
  - 병렬 체인 실행으로 응답 시간 단축
  - 체인 캐싱 및 메모리 최적화
  - 성능 목표 달성 확인 (≤10초, ≤30초, ≤5분)
  - LangChain 콜백을 통한 진행 상황 추적
  - _요구사항: 7 성능_

- [ ] 19. LangChain 기반 오류 처리 및 폴백 시스템
  - LangChain 체인 실행 오류 처리
  - 체인 재시도 로직 (최대 3회)
  - RAG 검색 실패 시 폴백 전략
  - 사용자 친화적 오류 메시지 표시
  - LangChain 로깅과 기존 로깅 시스템 통합
  - _요구사항: 6 로깅 & 안정성_

- [ ] 20. Docker 환경 구성 (LangChain 지원)
  - docker-compose.yml Local 환경 설정 (DynamoDB Local + MinIO + Chroma)
  - LangChain 의존성 포함 Dockerfile 설정
  - 환경 변수 설정 및 볼륨 마운트 구성
  - 헬스체크 엔드포인트 구현
  - 컨테이너 간 네트워크 설정
  - _요구사항: 5 환경별 실행_

- [ ] 21. 단위 테스트 작성 (LangChain 체인 테스트)
- [ ] 21.1 LangChain 체인 테스트
  - TextChains 클래스 단위 테스트 (Mock LLM 사용)
  - ImageChains 클래스 단위 테스트 (Mock 이미지 생성)
  - RAG 검색 체인 테스트 (Mock 벡터 스토어)
  - 체인 파이프라인 통합 테스트
  - _요구사항: 전체 시스템 안정성_

- [ ] 21.2 비즈니스 로직 및 저장소 테스트
  - BusinessService 클래스 테스트 (LangChain 체인 통합)
  - ImageOrchestrator 클래스 테스트 (체인 병렬 실행)
  - WorkflowManager 클래스 테스트 (체인 상태 관리)
  - DataInitializer 및 Storage 클래스 테스트
  - _요구사항: 전체 시스템 안정성_

- [ ] 21.3 UI 및 통합 테스트
  - Streamlit UI 컴포넌트 테스트 (각 단계별)
  - 전체 워크플로 통합 테스트 (5단계 완주)
  - 환경별 동작 테스트 (Local vs Dev)
  - LangChain 체인 성능 테스트 (SLA 목표 달성 확인)
  - _요구사항: 전체 시스템 안정성_

- [ ] 22. 성능 및 SLA 검증 (LangChain 최적화)
  - LangChain 체인 실행 성능 테스트
  - 상호명 생성 체인 성능 (≤10초)
  - 이미지 생성 체인 성능 (≤30초)
  - RAG 검색 체인 성능 (≤3초)
  - 전체 워크플로 성능 테스트 (≤5분)
  - _요구사항: 7 성능_

- [ ] 23. 문서화 및 배포 준비
  - README.md 작성 (LangChain 설치, 실행, 환경 설정 가이드)
  - LangChain 체인 구조 및 사용법 문서화
  - API 키 설정 가이드 작성 (OpenAI, AWS, Google)
  - Docker 실행 가이드 작성
  - 트러블슈팅 가이드 작성 (LangChain 관련 이슈 포함)
  - _요구사항: 전체 시스템 문서화_