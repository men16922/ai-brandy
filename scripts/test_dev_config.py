"""
Dev 환경 설정 테스트 (실제 AWS 연결 없이 설정만 확인)
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# dev 환경변수 로드
load_dotenv('.env.dev')

from storage.storage_factory import StorageManager


def test_dev_config():
    """Dev 환경 설정 테스트"""
    print("=== Dev Environment Configuration Test ===")
    
    # 환경변수 확인
    print("Environment Variables:")
    print(f"  APP_ENV: {os.getenv('APP_ENV')}")
    print(f"  AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'Not set')}")
    print(f"  AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION')}")
    print(f"  S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")
    print(f"  DYNAMODB_ENDPOINT: {os.getenv('DYNAMODB_ENDPOINT', 'Not set (using AWS)')}")
    print(f"  S3_ENDPOINT: {os.getenv('S3_ENDPOINT', 'Not set (using AWS)')}")
    print()
    
    try:
        # 저장소 매니저 초기화 (실제 연결은 하지 않음)
        manager = StorageManager()
        storage = manager.get_storage("dev")
        
        print("Storage Configuration:")
        print(f"  Environment: {storage.environment}")
        print(f"  Is Local: {storage.is_local}")
        print(f"  AWS Region: {storage.aws_region}")
        print(f"  Bucket Name: {storage.bucket_name}")
        print(f"  DynamoDB Endpoint: {storage.dynamodb_endpoint or 'AWS DynamoDB'}")
        print(f"  S3 Endpoint: {storage.s3_endpoint or 'AWS S3'}")
        print()
        
        print("Table Names:")
        for table_type, table_name in storage.table_names.items():
            print(f"  {table_type}: {table_name}")
        print()
        
        print("✅ Dev environment configuration loaded successfully!")
        print("📝 Note: This test only validates configuration, not actual AWS connectivity.")
        print("🔑 To test actual AWS connectivity, ensure valid AWS credentials are set.")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")


if __name__ == "__main__":
    test_dev_config()