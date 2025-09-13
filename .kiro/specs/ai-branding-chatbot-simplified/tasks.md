# 구현 계획 (처음부터 새로 구현)

- [x] 1. 프로젝트 기본 구조 및 환경 설정
  - 프로젝트 디렉토리 구조 생성
  - requirements.txt 작성 (Streamlit, boto3, openai, chromadb, reportlab 등)
  - .env 템플릿 파일 생성 (.env.local, .env.dev)
  - Docker 환경 설정 (docker-compose.yml for local)
  - 기본 설정 파일 구조 생성 (config/, data/, logs/, reports/)
  - _요구사항: 5 환경별 실행_

- [ ] 2. 로깅 시스템 구현
  - utils/logger.py 구조화된 로깅 클래스 작성
  - 환경별 로그 레벨 설정 (local: DEBUG, dev: INFO)
  - API 호출, 오류, 성능 메트릭 로깅 메서드 구현
  - 로그 파일 로테이션 및 보관 정책 구현
  - _요구사항: 6 로깅 & 안정성_

- [ ] 3. 환경별 저장소 시스템 구현
  - storage/storage_factory.py 환경별 저장소 팩토리 클래스 작성
  - storage/local_storage.py DynamoDB Local + 로컬 S3 연동 구현
  - storage/aws_storage.py AWS DynamoDB + AWS S3 연동 구현
  - 데이터 모델 클래스들 작성 (models/data_models.py)
  - 헬스체크 기능 구현 (환경별 서비스 상태 확인)
  - _요구사항: 5 환경별 실행_

- [ ] 3.1 JSON 데이터 DynamoDB 마이그레이션 시스템 구현
  - storage/data_initializer.py JSON → DynamoDB 마이그레이션 클래스 작성
  - DynamoDB 테이블 설계: brandy-regions-{env}, brandy-business-types-{env}
  - JSON 구조 변환 로직: 중첩 구조 → 평면 DynamoDB 아이템
  - 중복 방지 및 배치 삽입 로직 구현
  - 폴백 전략: DynamoDB 실패 시 JSON 파일 사용
  - _요구사항: 5 환경별 실행_

- [ ] 4. 핵심 비즈니스 서비스 구현
  - core/business_service.py 메인 비즈니스 로직 클래스 작성
  - 간단한 분석 로직 구현 (발음/검색 용이성 점수)
  - 상호명 생성 로직 구현 (중복 회피, 최대 3회 재생성)
  - 레이더 차트 데이터 생성 로직 구현
  - _요구사항: 1 상호명 추천_

- [ ] 5. AI 모델 어댑터 구현
  - adapters/text_adapter.py OpenAI 텍스트 생성 어댑터
  - adapters/dalle_adapter.py DALL-E 3 이미지 생성 어댑터
  - adapters/sdxl_adapter.py SDXL (Bedrock) 이미지 생성 어댑터
  - adapters/gemini_adapter.py Gemini Flash 2.5 이미지 생성 어댑터
  - 폴백 이미지 처리 로직 구현
  - API 오류 처리 및 재시도 로직 구현
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 6. 이미지 생성 오케스트레이터 구현
  - core/image_orchestrator.py 이미지 생성 통합 관리 클래스
  - 간판 이미지 3안 생성 (DALL-E/SDXL/Gemini 병렬 호출)
  - 인테리어 이미지 3안 생성 (선택된 간판과 조화)
  - 색상 팔레트 추출 및 예산 범위 계산 로직
  - 폴백 이미지 제공 및 오류 처리
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 7. PDF 보고서 생성 시스템 구현
  - core/pdf_generator.py PDF 보고서 생성 클래스
  - 보고서 템플릿 설계 (상호명, 이미지, 색상 팔레트, 예산, 분석 요약)
  - 이미지 썸네일 생성 및 레이아웃 구성
  - 선택 표시 기능 (선택된 간판/인테리어 하이라이트)
  - PDF 파일 저장 및 다운로드 링크 생성
  - _요구사항: 4 보고서 생성_

- [ ] 8. 벡터 저장소 시스템 구현
  - vector/vector_store_factory.py 환경별 벡터 스토어 팩토리
  - vector/chroma_store.py Chroma DB 연동 (Local 환경)
  - vector/bedrock_store.py Bedrock Knowledge Base 연동 (Dev 환경)
  - PDF 보고서 벡터화 및 저장 로직
  - 벡터 검색 및 유사도 계산 기능
  - _요구사항: 5 환경별 실행_

- [ ] 9. 워크플로 관리자 구현
  - core/workflow_manager.py 5단계 워크플로 상태 관리
  - DynamoDB 기반 세션 관리 (brandy-sessions-{env} 테이블)
  - 단계별 진행 상태 추적 및 데이터 저장
  - 재생성 횟수 제한 관리 (상호명 최대 3회)
  - 진행률 계산 및 ETA 추정 로직
  - _요구사항: 전체 워크플로_

- [ ] 10. Streamlit UI 구현 - 1단계: 정보 입력
  - app.py 메인 애플리케이션 진입점 및 초기화
  - 1단계 UI: 업종/지역/평수 입력 폼
  - 사진 업로드 옵션 구현 (선택사항)
  - DynamoDB에서 지역/업종 데이터 로드 및 자동완성
  - 입력 검증 및 다음 단계 진행 버튼
  - _요구사항: 1 상호명 추천_

- [ ] 11. Streamlit UI 구현 - 2단계: 분석 요약
  - 2단계 UI: 분석 결과 표시
  - 점수 표시 (발음/검색 용이성)
  - Plotly 레이더 차트 구현
  - 분석 요약 텍스트 표시
  - 다음 단계 진행 버튼
  - _요구사항: 1 상호명 추천_

- [ ] 12. Streamlit UI 구현 - 3단계: 상호명 제안
  - 3단계 UI: 상호명 3개 추천 표시
  - 각 상호명별 설명 및 점수 카드 형태 표시
  - 선택 버튼 및 재추천 버튼 (최대 3회)
  - 재추천 시 중복 회피 로직 연동
  - 진행 상황 표시 (로딩 스피너 + ETA)
  - _요구사항: 1 상호명 추천_

- [ ] 13. Streamlit UI 구현 - 4단계: 이미지 생성
  - 4단계 UI: 간판 + 인테리어 이미지 생성 및 표시
  - 간판 3안 카드 형태 표시 (DALL-E/SDXL/Gemini)
  - 인테리어 3안 카드 형태 표시 (색상 팔레트 + 예산 포함)
  - 폴백 이미지 처리 및 오류 메시지 표시
  - 이미지 생성 진행 상황 표시 (30초 타이머)
  - _요구사항: 2 간판 이미지 생성, 3 인테리어 추천_

- [ ] 14. Streamlit UI 구현 - 5단계: 보고서 생성
  - 5단계 UI: PDF 보고서 생성 및 다운로드
  - 보고서 생성 진행 상황 표시
  - PDF 다운로드 버튼 구현
  - 보고서 미리보기 기능 (선택사항)
  - 벡터화 완료 상태 표시
  - _요구사항: 4 보고서 생성_

- [ ] 15. 진행 상황 및 성능 최적화
  - 전체 워크플로 진행률 표시 (1-5단계)
  - ETA 계산 및 표시 로직 구현
  - 로딩 스피너 및 진행 바 구현
  - 성능 목표 달성 확인 (≤10초, ≤30초, ≤5분)
  - 타임아웃 처리 및 오류 복구 로직
  - _요구사항: 7 성능_

- [ ] 16. 오류 처리 및 폴백 시스템 구현
  - API 호출 실패 시 폴백 데이터/이미지 제공
  - 네트워크 오류 시 재시도 로직 (최대 3회)
  - 사용자 친화적 오류 메시지 표시
  - 시스템 복구 및 상태 복원 로직
  - 로그 기반 오류 추적 및 디버깅 지원
  - _요구사항: 6 로깅 & 안정성_

- [ ] 17. Docker 환경 구성
  - docker-compose.yml Local 환경 설정 (DynamoDB Local + Chroma)
  - Dockerfile 애플리케이션 컨테이너 설정
  - 환경 변수 설정 및 볼륨 마운트 구성
  - 헬스체크 엔드포인트 구현
  - 컨테이너 간 네트워크 설정
  - _요구사항: 5 환경별 실행_

- [ ] 18. 단위 테스트 작성
- [ ] 18.1 핵심 비즈니스 로직 테스트
  - BusinessService 클래스 단위 테스트 (상호명 생성, 분석 로직)
  - ImageOrchestrator 클래스 단위 테스트 (이미지 생성 로직)
  - PDFGenerator 클래스 단위 테스트 (보고서 생성)
  - WorkflowManager 클래스 단위 테스트 (상태 관리)
  - _요구사항: 전체 시스템 안정성_

- [ ] 18.2 저장소 및 어댑터 테스트
  - DataInitializer 클래스 테스트 (JSON → DynamoDB 마이그레이션)
  - StorageFactory 및 환경별 Storage 클래스 테스트
  - AI 모델 어댑터 클래스들 테스트 (Mock API 사용)
  - VectorStoreFactory 및 벡터 스토어 테스트
  - _요구사항: 전체 시스템 안정성_

- [ ] 18.3 UI 및 통합 테스트
  - Streamlit UI 컴포넌트 테스트 (각 단계별)
  - 전체 워크플로 통합 테스트 (5단계 완주)
  - 환경별 동작 테스트 (Local vs Dev)
  - 성능 테스트 (SLA 목표 달성 확인)
  - _요구사항: 전체 시스템 안정성_

- [ ] 19. 성능 및 SLA 검증
  - 상호명 생성 성능 테스트 (≤10초)
  - 이미지 생성 성능 테스트 (≤30초)
  - 전체 워크플로 성능 테스트 (≤5분)
  - 텍스트 응답 성능 테스트 (≤5초)
  - 동시 사용자 부하 테스트 (선택사항)
  - _요구사항: 7 성능_

- [ ] 20. 문서화 및 배포 준비
  - README.md 작성 (설치, 실행, 환경 설정 가이드)
  - API 키 설정 가이드 작성
  - Docker 실행 가이드 작성
  - 트러블슈팅 가이드 작성
  - 시연 시나리오 스크립트 작성
  - _요구사항: 전체 시스템 문서화_