"""
애플리케이션 전역 설정 관리
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


class AppConfig:
    """애플리케이션 설정 클래스"""
    
    def __init__(self, environment: str = None):
        """
        설정 초기화
        
        Args:
            environment: 환경 설정 (local/dev)
        """
        self.environment = environment or os.getenv("APP_ENV", "local")
        self.load_environment_variables()
        
    def load_environment_variables(self):
        """환경별 .env 파일 로드"""
        env_file = f".env.{self.environment}"
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded environment variables from {env_file}")
        else:
            print(f"Environment file {env_file} not found, using system environment variables")
            
    @property
    def is_local(self) -> bool:
        """로컬 환경 여부"""
        return self.environment == "local"
        
    @property
    def is_dev(self) -> bool:
        """개발 환경 여부"""
        return self.environment == "dev"
        
    @property
    def debug_mode(self) -> bool:
        """디버그 모드 여부"""
        return os.getenv("DEBUG_MODE", "false").lower() == "true"
        
    @property
    def log_level(self) -> str:
        """로그 레벨"""
        return os.getenv("LOG_LEVEL", "INFO")
        
    def get_database_config(self) -> Dict[str, Any]:
        """데이터베이스 설정 반환"""
        if self.is_local:
            return {
                "dynamodb_endpoint": os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000"),
                "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            }
        else:
            return {
                "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                "s3_bucket": os.getenv("S3_BUCKET_NAME", "ai-branding-dev")
            }
            
    def get_storage_config(self) -> Dict[str, Any]:
        """저장소 설정 반환 (S3/MinIO)"""
        if self.is_local:
            return {
                "type": "minio",
                "endpoint": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
                "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                "bucket_name": os.getenv("MINIO_BUCKET_NAME", "ai-branding-local"),
                "base_images_bucket": os.getenv("BASE_IMAGES_BUCKET", "branding-base-images-local")
            }
        else:
            return {
                "type": "s3",
                "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                "bucket_name": os.getenv("S3_BUCKET_NAME", "ai-branding-dev"),
                "base_images_bucket": os.getenv("S3_BASE_IMAGES_BUCKET", "branding-base-images-dev")
            }
            
    def get_vector_store_config(self) -> Dict[str, Any]:
        """벡터 스토어 설정 반환"""
        if self.is_local:
            return {
                "type": "chroma",
                "persist_directory": os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db"),
                "collection_name": os.getenv("CHROMA_COLLECTION_NAME", "branding_knowledge")
            }
        else:
            return {
                "type": "bedrock",
                "knowledge_base_id": os.getenv("BEDROCK_KNOWLEDGE_BASE_ID"),
                "region": os.getenv("BEDROCK_REGION", "us-east-1")
            }
            
    def get_storage_paths(self) -> Dict[str, str]:
        """저장소 경로 설정 반환"""
        return {
            "data_dir": os.getenv("LOCAL_DATA_DIR", "./data"),
            "logs_dir": os.getenv("LOCAL_LOGS_DIR", "./logs"),
            "reports_dir": os.getenv("LOCAL_REPORTS_DIR", "./reports"),
            "images_dir": os.getenv("LOCAL_IMAGES_DIR", "./data/images")
        }


# 전역 설정 인스턴스
_app_config = None


def get_app_config(environment: str = None) -> AppConfig:
    """애플리케이션 설정 싱글톤 인스턴스 반환"""
    global _app_config
    
    if _app_config is None:
        _app_config = AppConfig(environment)
        
    return _app_config