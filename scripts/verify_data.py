"""
DynamoDB에 저장된 데이터 확인 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경변수 로드
load_dotenv('.env.local')

from storage.storage_factory import StorageManager


def verify_dynamodb_data():
    """DynamoDB에 저장된 데이터 확인"""
    print("=== DynamoDB Data Verification ===")
    
    # 저장소 매니저 초기화
    manager = StorageManager()
    storage = manager.get_storage("local")
    
    print(f"Environment: {storage.environment}")
    print(f"DynamoDB Endpoint: {storage.dynamodb_endpoint}")
    print(f"S3 Endpoint: {storage.s3_endpoint}")
    print(f"Bucket Name: {storage.bucket_name}")
    print()
    
    # 지역 데이터 확인
    print("--- Regions Data ---")
    regions = storage.get_regions()
    if regions:
        for region, districts in regions.items():
            print(f"📍 {region}:")
            for district, info in districts.items():
                print(f"  • {district}: {info['characteristics'][:2]}... (유동인구: {info['foot_traffic']}, 임대료: {info['rent_level']})")
    else:
        print("❌ No regions data found")
    
    print()
    
    # 업종 데이터 확인
    print("--- Business Types Data ---")
    business_types = storage.get_business_types()
    if business_types:
        for business_type, info in business_types.items():
            print(f"🏪 {business_type}:")
            print(f"  • 키워드: {info['keywords'][:3]}...")
            print(f"  • 평수 범위: {info['typical_size'][0]}~{info['typical_size'][1]}평")
            print(f"  • 스타일: {info['style_suggestions'][:2]}...")
    else:
        print("❌ No business types data found")
    
    print()
    
    # 테이블 직접 조회 (DynamoDB 원본 데이터)
    print("--- Raw DynamoDB Data ---")
    try:
        # 지역 테이블 직접 조회
        regions_table = storage.dynamodb.Table(storage.table_names["regions"])
        regions_response = regions_table.scan(Limit=3)
        print(f"Regions table items (showing first 3):")
        for item in regions_response.get('Items', []):
            print(f"  PK: {item['PK']}, SK: {item['SK']}")
            print(f"  Region: {item['region']}, District: {item['district']}")
            print(f"  Characteristics: {item['characteristics']}")
            print()
        
        # 업종 테이블 직접 조회
        business_types_table = storage.dynamodb.Table(storage.table_names["business_types"])
        business_types_response = business_types_table.scan(Limit=2)
        print(f"Business types table items (showing first 2):")
        for item in business_types_response.get('Items', []):
            print(f"  PK: {item['PK']}, SK: {item['SK']}")
            print(f"  Business Type: {item['business_type']}")
            print(f"  Keywords: {item['keywords']}")
            print()
            
    except Exception as e:
        print(f"❌ Error accessing raw DynamoDB data: {str(e)}")
    
    # 헬스체크
    print("--- Health Check ---")
    health_results = storage.health_check()
    for result in health_results:
        status_icon = "✅" if result.status == "healthy" else "❌"
        print(f"{status_icon} {result.service_name}: {result.status}")
        print(f"   Message: {result.message}")
        if result.response_time_ms:
            print(f"   Response Time: {result.response_time_ms:.2f}ms")
        print()


if __name__ == "__main__":
    verify_dynamodb_data()