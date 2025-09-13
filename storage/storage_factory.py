"""
환경별 저장소 팩토리
환경에 따라 적절한 저장소 구현체를 생성
"""

import os
import logging
from typing import Optional
from models.data_models import Environment
from storage.base_storage import BaseStorage
from storage.unified_storage import UnifiedStorage


class StorageFactory:
    """저장소 팩토리 클래스"""
    
    @staticmethod
    def create_storage(environment: Optional[str] = None) -> BaseStorage:
        """환경에 맞는 저장소 클라이언트 생성
        
        Args:
            environment: 환경 설정 (local, dev). None인 경우 환경변수에서 읽음
            
        Returns:
            BaseStorage: 환경에 맞는 저장소 구현체
            
        Raises:
            ValueError: 지원하지 않는 환경인 경우
        """
        logger = logging.getLogger(__name__)
        
        # 환경 설정 결정
        if environment is None:
            environment = os.getenv('APP_ENV', 'local').lower()
        
        logger.info(f"Creating storage for environment: {environment}")
        
        # 통합 저장소 생성 (환경변수 기반 자동 설정)
        if environment in [e.value for e in Environment]:
            return UnifiedStorage(environment)
        else:
            raise ValueError(f"Unsupported environment: {environment}. Supported: {[e.value for e in Environment]}")
    
    @staticmethod
    def get_supported_environments() -> list[str]:
        """지원하는 환경 목록 반환"""
        return [e.value for e in Environment]
    
    @staticmethod
    def validate_environment(environment: str) -> bool:
        """환경 설정 유효성 검증"""
        return environment.lower() in [e.value for e in Environment]


class StorageManager:
    """저장소 관리자 - 싱글톤 패턴으로 저장소 인스턴스 관리"""
    
    _instance = None
    _storage = None
    _current_environment = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
        return cls._instance
    
    def get_storage(self, environment: Optional[str] = None) -> BaseStorage:
        """저장소 인스턴스 반환 (캐싱)
        
        Args:
            environment: 환경 설정
            
        Returns:
            BaseStorage: 저장소 인스턴스
        """
        if environment is None:
            environment = os.getenv('APP_ENV', 'local').lower()
        
        # 환경이 변경되었거나 처음 생성하는 경우
        if self._storage is None or self._current_environment != environment:
            self._storage = StorageFactory.create_storage(environment)
            self._current_environment = environment
        
        return self._storage
    
    def reset(self):
        """저장소 인스턴스 초기화 (테스트용)"""
        self._storage = None
        self._current_environment = None