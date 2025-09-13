"""
데이터 모델 정의
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class BusinessInfo:
    """비즈니스 정보"""
    business_type: str      # 업종
    location: str          # 지역
    size: int             # 평수
    keywords: List[str]   # 스타일 키워드
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class BusinessName:
    """상호명 후보"""
    name: str             # 상호명
    description: str      # 설명
    scores: Dict[str, float]  # 세부 점수
    total_score: float    # 총점
    rationale: List[str]  # 점수 근거
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AnalysisResult:
    """다차원 분석 결과"""
    candidates: List[BusinessName]  # 분석된 상호명 후보들
    top3: List[str]                # 상위 3개 상호명
    analysis_summary: Dict[str, Any]  # 분석 요약
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ImageResult:
    """이미지 생성 결과"""
    image_url: str       # 이미지 URL
    prompt: str          # 생성 프롬프트
    model_name: str      # 사용된 AI 모델
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Session:
    """세션 데이터"""
    session_id: str
    current_step: int = 1
    business_info: Optional[BusinessInfo] = None
    analysis_result: Optional[AnalysisResult] = None
    selected_name: Optional[str] = None
    sign_designs: List[ImageResult] = None
    interior_designs: List[ImageResult] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.sign_designs is None:
            self.sign_designs = []
        if self.interior_designs is None:
            self.interior_designs = []