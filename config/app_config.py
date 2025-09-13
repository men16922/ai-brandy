"""
Application Configuration Module
환경별 설정 관리 및 검증
"""

import os
from typing import Optional, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from enum import Enum


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class VectorStoreType(str, Enum):
    CHROMA = "chroma"
    BEDROCK = "bedrock"


class AppConfig(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # Environment
    app_env: Environment = Field(default=Environment.LOCAL, env="APP_ENV")
    debug_mode: bool = Field(default=True, env="DEBUG_MODE")
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field(default="us-east-1", env="AWS_DEFAULT_REGION")
    aws_endpoint_url: Optional[str] = Field(None, env="AWS_ENDPOINT_URL")
    
    # Storage Configuration
    s3_bucket_name: str = Field(..., env="S3_BUCKET_NAME")
    dynamodb_table_prefix: str = Field(default="brandy", env="DYNAMODB_TABLE_PREFIX")
    dynamodb_endpoint_url: Optional[str] = Field(None, env="DYNAMODB_ENDPOINT_URL")
    
    # Vector Database
    vector_store_type: VectorStoreType = Field(default=VectorStoreType.CHROMA, env="VECTOR_STORE_TYPE")
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8001, env="CHROMA_PORT")
    bedrock_knowledge_base_id: Optional[str] = Field(None, env="BEDROCK_KNOWLEDGE_BASE_ID")
    bedrock_region: str = Field(default="us-east-1", env="BEDROCK_REGION")
    
    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_regeneration_count: int = Field(default=3, env="MAX_REGENERATION_COUNT")
    
    # Directories
    data_dir: str = Field(default="./data", env="DATA_DIR")
    logs_dir: str = Field(default="./logs", env="LOGS_DIR")
    reports_dir: str = Field(default="./reports", env="REPORTS_DIR")
    config_dir: str = Field(default="./config", env="CONFIG_DIR")
    
    # Performance Settings
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    image_generation_timeout: int = Field(default=60, env="IMAGE_GENERATION_TIMEOUT")
    pdf_generation_timeout: int = Field(default=20, env="PDF_GENERATION_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("app_env", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("vector_store_type", pre=True)
    def validate_vector_store_type(cls, v):
        if isinstance(v, str):
            return VectorStoreType(v.lower())
        return v
    
    def get_dynamodb_table_name(self, table_type: str) -> str:
        """DynamoDB 테이블명 생성"""
        return f"{self.dynamodb_table_prefix}-{table_type}-{self.app_env.value}"
    
    def get_s3_key_prefix(self, key_type: str) -> str:
        """S3 키 프리픽스 생성"""
        return f"{self.app_env.value}/{key_type}"
    
    def is_local_environment(self) -> bool:
        """로컬 환경 여부 확인"""
        return self.app_env == Environment.LOCAL
    
    def is_dev_environment(self) -> bool:
        """개발 환경 여부 확인"""
        return self.app_env == Environment.DEV


def load_config() -> AppConfig:
    """환경별 설정 로드"""
    env = os.getenv("APP_ENV", "local").lower()
    
    # 환경별 .env 파일 로드
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        return AppConfig(_env_file=env_file)
    else:
        return AppConfig()


# Global configuration instance
config = load_config()