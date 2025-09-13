"""
기본 저장소 인터페이스
모든 저장소 구현체가 상속받아야 하는 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from models.data_models import HealthCheckResult


class BaseStorage(ABC):
    """저장소 기본 인터페이스"""
    
    def __init__(self, environment: str):
        self.environment = environment
    
    @abstractmethod
    def save_chat_history(self, session_id: str, message: Dict[str, Any]) -> bool:
        """채팅 이력 저장"""
        pass
    
    @abstractmethod
    def save_image(self, image_data: bytes, key: str) -> str:
        """이미지 저장"""
        pass
    
    @abstractmethod
    def upload_to_vector_store(self, file_path: str, metadata: Dict[str, Any]) -> str:
        """벡터 스토어에 파일 업로드"""
        pass
    
    @abstractmethod
    def get_regions(self) -> Dict[str, Any]:
        """지역 데이터 조회"""
        pass
    
    @abstractmethod
    def get_business_types(self) -> Dict[str, Any]:
        """업종 데이터 조회"""
        pass
    
    @abstractmethod
    def save_workflow_session(self, session_data: Dict[str, Any]) -> bool:
        """워크플로 세션 저장"""
        pass
    
    @abstractmethod
    def get_workflow_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """워크플로 세션 조회"""
        pass
    
    @abstractmethod
    def update_workflow_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """워크플로 세션 업데이트"""
        pass
    
    @abstractmethod
    def health_check(self) -> List[HealthCheckResult]:
        """헬스체크 수행"""
        pass
    
    @abstractmethod
    def initialize_tables(self) -> bool:
        """테이블 초기화"""
        pass