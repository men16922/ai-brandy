"""
데이터 모델 클래스들
AI 브랜딩 챗봇 시스템의 모든 데이터 모델을 정의
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class Environment(Enum):
    """환경 구분"""
    LOCAL = "local"
    DEV = "dev"


@dataclass
class RegionData:
    """지역 데이터 모델 (DynamoDB 마이그레이션용)"""
    region: str                    # 지역명 (서울, 인천, 경기)
    district: str                  # 구역명 (강남, 홍대, 명동)
    characteristics: List[str]     # 특성 리스트
    foot_traffic: str             # 유동인구 수준
    rent_level: str               # 임대료 수준
    created_at: datetime = field(default_factory=datetime.now)
    data_source: str = "regions.json"
    
    def to_dynamodb_item(self, env: str) -> Dict[str, Any]:
        """DynamoDB 아이템 형식으로 변환"""
        return {
            "PK": f"REGION#{self.region}",
            "SK": f"DISTRICT#{self.district}",
            "region": self.region,
            "district": self.district,
            "characteristics": self.characteristics,
            "foot_traffic": self.foot_traffic,
            "rent_level": self.rent_level,
            "created_at": self.created_at.isoformat(),
            "data_source": self.data_source
        }


@dataclass
class BusinessTypeData:
    """업종 데이터 모델 (DynamoDB 마이그레이션용)"""
    business_type: str            # 업종명 (카페, 네일샵, 헤어샵)
    keywords: List[str]           # 관련 키워드
    typical_size: List[int]       # 일반적인 평수 범위 [최소, 최대]
    style_suggestions: List[str]  # 스타일 제안
    created_at: datetime = field(default_factory=datetime.now)
    data_source: str = "business_types.json"
    
    def to_dynamodb_item(self, env: str) -> Dict[str, Any]:
        """DynamoDB 아이템 형식으로 변환"""
        return {
            "PK": f"BUSINESS_TYPE#{self.business_type}",
            "SK": "METADATA",
            "business_type": self.business_type,
            "keywords": self.keywords,
            "typical_size": self.typical_size,
            "style_suggestions": self.style_suggestions,
            "created_at": self.created_at.isoformat(),
            "data_source": self.data_source
        }


@dataclass
class WorkflowSession:
    """워크플로 세션 모델"""
    session_id: str
    current_step: int = 1         # 1-5
    business_info: Dict = field(default_factory=dict)  # 업종/지역/평수
    uploaded_photo: Optional[str] = None  # 업로드된 사진 경로
    analysis_result: Dict = field(default_factory=dict)  # 분석 결과
    business_names: List[Dict] = field(default_factory=list)  # 생성된 상호명들
    selected_name: Optional[str] = None  # 선택된 상호명
    regeneration_count: int = 0   # 재생성 횟수 (최대 3)
    sign_images: List[Dict] = field(default_factory=list)  # 간판 이미지 3안
    interior_images: List[Dict] = field(default_factory=list)  # 인테리어 이미지 3안
    pdf_report_path: Optional[str] = None  # 생성된 PDF 경로
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dynamodb_item(self, env: str) -> Dict[str, Any]:
        """DynamoDB 아이템 형식으로 변환"""
        return {
            "PK": f"SESSION#{self.session_id}",
            "SK": "METADATA",
            "session_id": self.session_id,
            "current_step": self.current_step,
            "business_info": self.business_info,
            "uploaded_photo": self.uploaded_photo,
            "analysis_result": self.analysis_result,
            "business_names": self.business_names,
            "selected_name": self.selected_name,
            "regeneration_count": self.regeneration_count,
            "sign_images": self.sign_images,
            "interior_images": self.interior_images,
            "pdf_report_path": self.pdf_report_path,
            "GSI1PK": f"STATUS#active",
            "GSI1SK": self.created_at.isoformat(),
            "version": "1.0",
            "expire_at": int((self.created_at.timestamp() + 86400)),  # 24시간 TTL
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class BusinessInfo:
    """비즈니스 정보"""
    business_type: str      # 업종 (DynamoDB에서 조회)
    location: str          # 지역 (DynamoDB에서 조회)
    size: int             # 평수
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BusinessName:
    """상호명 후보"""
    name: str             # 상호명
    description: str      # 간단 설명
    scores: Dict[str, int] = field(default_factory=dict)  # 점수 {"발음": 85, "검색": 90}
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisResult:
    """분석 결과"""
    scores: Dict = field(default_factory=dict)              # 전체 점수
    radar_chart_data: Dict = field(default_factory=dict)    # 레이더 차트용 데이터
    summary: str = ""              # 분석 요약
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImageDesign:
    """이미지 디자인"""
    design_type: str      # "sign" 또는 "interior"
    business_name: str    # 상호명
    image_url: str       # 이미지 파일 경로
    fallback_url: str    # 폴백 이미지 경로
    model_name: str      # 사용된 AI 모델명 (DALL-E/SDXL/Gemini)
    description: str     # 간단 설명
    color_palette: List[str] = field(default_factory=list)  # 색상 팔레트 (인테리어용)
    estimated_budget: Optional[str] = None  # 예산 범위 (인테리어용)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PDFReport:
    """PDF 보고서"""
    session_id: str
    business_name: str           # 최종 선택된 상호명
    sign_designs: List[ImageDesign] = field(default_factory=list)    # 간판 3안
    interior_designs: List[ImageDesign] = field(default_factory=list) # 인테리어 3안
    selected_sign: Optional[str] = None       # 선택된 간판 (표시용)
    selected_interior: Optional[str] = None   # 선택된 인테리어 (표시용)
    color_palette: List[str] = field(default_factory=list)           # 전체 색상 팔레트
    budget_range: str = ""                  # 예산 범위
    analysis_summary: str = ""              # 분석 요약
    pdf_path: str = ""                      # 생성된 PDF 파일 경로
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheckResult:
    """헬스체크 결과"""
    service_name: str
    status: str  # "healthy", "unhealthy", "unknown"
    message: str
    response_time_ms: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 형태로 변환"""
        return {
            "service_name": self.service_name,
            "status": self.status,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat()
        }