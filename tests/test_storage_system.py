"""
저장소 시스템 테스트
환경별 저장소 구현체와 데이터 마이그레이션 테스트
"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.storage_factory import StorageFactory, StorageManager
from storage.data_initializer import DataInitializer
from models.data_models import WorkflowSession


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_storage_factory():
    """저장소 팩토리 테스트"""
    print("=== Storage Factory Test ===")
    
    # 지원 환경 확인
    environments = StorageFactory.get_supported_environments()
    print(f"Supported environments: {environments}")
    
    # 환경별 저장소 생성 테스트
    for env in environments:
        try:
            storage = StorageFactory.create_storage(env)
            print(f"✓ Created {env} storage: {type(storage).__name__}")
        except Exception as e:
            print(f"✗ Failed to create {env} storage: {str(e)}")
    
    # 잘못된 환경 테스트
    try:
        StorageFactory.create_storage("invalid")
        print("✗ Should have failed for invalid environment")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid environment: {str(e)}")


def test_storage_manager():
    """저장소 매니저 테스트"""
    print("\n=== Storage Manager Test ===")
    
    manager1 = StorageManager()
    manager2 = StorageManager()
    
    # 싱글톤 패턴 확인
    if manager1 is manager2:
        print("✓ StorageManager is singleton")
    else:
        print("✗ StorageManager is not singleton")
    
    # 저장소 인스턴스 캐싱 확인
    storage1 = manager1.get_storage("local")
    storage2 = manager1.get_storage("local")
    
    if storage1 is storage2:
        print("✓ Storage instance is cached")
    else:
        print("✗ Storage instance is not cached")


def test_data_models():
    """데이터 모델 테스트"""
    print("\n=== Data Models Test ===")
    
    # WorkflowSession 모델 테스트
    session = WorkflowSession(
        session_id="test-session-123",
        current_step=1,
        business_info={"type": "카페", "location": "강남", "size": 20}
    )
    
    # DynamoDB 아이템 변환 테스트
    dynamodb_item = session.to_dynamodb_item("local")
    
    expected_keys = ['PK', 'SK', 'session_id', 'current_step', 'business_info', 'GSI1PK', 'GSI1SK']
    missing_keys = [key for key in expected_keys if key not in dynamodb_item]
    
    if not missing_keys:
        print("✓ WorkflowSession to DynamoDB conversion successful")
        print(f"  - PK: {dynamodb_item['PK']}")
        print(f"  - SK: {dynamodb_item['SK']}")
        print(f"  - GSI1PK: {dynamodb_item['GSI1PK']}")
    else:
        print(f"✗ Missing keys in DynamoDB item: {missing_keys}")


def test_data_initializer_structure():
    """데이터 초기화 구조 테스트 (실제 DB 연결 없이)"""
    print("\n=== Data Initializer Structure Test ===")
    
    try:
        # 로컬 저장소 생성 (실제 연결은 하지 않음)
        storage = StorageFactory.create_storage("local")
        initializer = DataInitializer(storage, "local")
        
        print("✓ DataInitializer created successfully")
        
        # JSON 파일 존재 확인
        import os
        regions_file = os.path.join("data", "regions.json")
        business_types_file = os.path.join("data", "business_types.json")
        
        if os.path.exists(regions_file):
            print("✓ regions.json file exists")
        else:
            print("✗ regions.json file not found")
        
        if os.path.exists(business_types_file):
            print("✓ business_types.json file exists")
        else:
            print("✗ business_types.json file not found")
        
        # 폴백 데이터 로드 테스트
        regions_data = initializer.get_fallback_regions()
        business_types_data = initializer.get_fallback_business_types()
        
        if regions_data:
            print(f"✓ Loaded {len(regions_data)} regions from fallback")
        else:
            print("✗ Failed to load regions from fallback")
        
        if business_types_data:
            print(f"✓ Loaded {len(business_types_data)} business types from fallback")
        else:
            print("✗ Failed to load business types from fallback")
            
    except Exception as e:
        print(f"✗ DataInitializer test failed: {str(e)}")


def test_health_check_structure():
    """헬스체크 구조 테스트"""
    print("\n=== Health Check Structure Test ===")
    
    try:
        from models.data_models import HealthCheckResult
        
        # 헬스체크 결과 생성 테스트
        result = HealthCheckResult(
            service_name="Test Service",
            status="healthy",
            message="Test message",
            response_time_ms=100.5
        )
        
        result_dict = result.to_dict()
        expected_keys = ['service_name', 'status', 'message', 'response_time_ms', 'timestamp']
        missing_keys = [key for key in expected_keys if key not in result_dict]
        
        if not missing_keys:
            print("✓ HealthCheckResult structure is correct")
            print(f"  - Service: {result_dict['service_name']}")
            print(f"  - Status: {result_dict['status']}")
            print(f"  - Response Time: {result_dict['response_time_ms']}ms")
        else:
            print(f"✗ Missing keys in HealthCheckResult: {missing_keys}")
            
    except Exception as e:
        print(f"✗ HealthCheckResult test failed: {str(e)}")


def main():
    """메인 테스트 함수"""
    setup_logging()
    
    print("Storage System Test Suite")
    print("=" * 50)
    
    test_storage_factory()
    test_storage_manager()
    test_data_models()
    test_data_initializer_structure()
    test_health_check_structure()
    
    print("\n" + "=" * 50)
    print("Test completed. Check results above.")
    print("Note: This test does not require actual database connections.")


if __name__ == "__main__":
    main()