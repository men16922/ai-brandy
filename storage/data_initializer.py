"""
JSON 데이터 DynamoDB 마이그레이션 시스템
data/ 폴더의 JSON 파일들을 DynamoDB 테이블로 마이그레이션
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from models.data_models import RegionData, BusinessTypeData
from storage.base_storage import BaseStorage


class DataInitializer:
    """JSON → DynamoDB 마이그레이션 클래스"""
    
    def __init__(self, storage: BaseStorage, environment: str):
        self.storage = storage
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self.data_dir = "data"
        
    def initialize_all_data(self) -> bool:
        """모든 초기 데이터 로드 (regions.json + business_types.json)"""
        try:
            self.logger.info(f"Starting data initialization for {self.environment} environment")
            
            # 테이블 초기화
            if not self.storage.initialize_tables():
                self.logger.error("Failed to initialize tables")
                return False
            
            # 지역 데이터 로드
            regions_success = self.load_regions_data()
            if not regions_success:
                self.logger.warning("Failed to load regions data, will fallback to JSON")
            
            # 업종 데이터 로드
            business_types_success = self.load_business_types_data()
            if not business_types_success:
                self.logger.warning("Failed to load business types data, will fallback to JSON")
            
            success = regions_success and business_types_success
            if success:
                self.logger.info("Data initialization completed successfully")
            else:
                self.logger.warning("Data initialization completed with warnings")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Data initialization failed: {str(e)}")
            return False
    
    def load_regions_data(self) -> bool:
        """regions.json 데이터를 DynamoDB에 로드"""
        try:
            table_name = f"brandy-regions-{self.environment}"
            
            # 데이터가 이미 존재하는지 확인
            if self.check_data_exists(table_name):
                self.logger.info(f"Regions data already exists in {table_name}")
                return True
            
            # JSON 파일 읽기
            regions_file = os.path.join(self.data_dir, "regions.json")
            if not os.path.exists(regions_file):
                self.logger.error(f"Regions file not found: {regions_file}")
                return False
            
            with open(regions_file, 'r', encoding='utf-8') as f:
                regions_data = json.load(f)
            
            # DynamoDB 아이템으로 변환
            items = self._convert_regions_to_dynamodb_items(regions_data)
            
            # 배치 삽입
            success_count = self._batch_write_items(table_name, items)
            
            self.logger.info(f"Loaded {success_count}/{len(items)} regions items to {table_name}")
            return success_count == len(items)
            
        except Exception as e:
            self.logger.error(f"Failed to load regions data: {str(e)}")
            return False
    
    def load_business_types_data(self) -> bool:
        """business_types.json 데이터를 DynamoDB에 로드"""
        try:
            table_name = f"brandy-business-types-{self.environment}"
            
            # 데이터가 이미 존재하는지 확인
            if self.check_data_exists(table_name):
                self.logger.info(f"Business types data already exists in {table_name}")
                return True
            
            # JSON 파일 읽기
            business_types_file = os.path.join(self.data_dir, "business_types.json")
            if not os.path.exists(business_types_file):
                self.logger.error(f"Business types file not found: {business_types_file}")
                return False
            
            with open(business_types_file, 'r', encoding='utf-8') as f:
                business_types_data = json.load(f)
            
            # DynamoDB 아이템으로 변환
            items = self._convert_business_types_to_dynamodb_items(business_types_data)
            
            # 배치 삽입
            success_count = self._batch_write_items(table_name, items)
            
            self.logger.info(f"Loaded {success_count}/{len(items)} business types items to {table_name}")
            return success_count == len(items)
            
        except Exception as e:
            self.logger.error(f"Failed to load business types data: {str(e)}")
            return False
    
    def check_data_exists(self, table_name: str) -> bool:
        """테이블에 데이터가 이미 존재하는지 확인"""
        try:
            # 저장소별 구현에 위임
            if hasattr(self.storage, '_check_table_has_data'):
                return self.storage._check_table_has_data(table_name)
            return False
        except Exception as e:
            self.logger.warning(f"Could not check if data exists in {table_name}: {str(e)}")
            return False
    
    def _convert_regions_to_dynamodb_items(self, regions_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """regions.json 구조를 DynamoDB 아이템으로 변환"""
        items = []
        
        for region, districts in regions_data.items():
            for district, info in districts.items():
                region_data = RegionData(
                    region=region,
                    district=district,
                    characteristics=info.get("characteristics", []),
                    foot_traffic=info.get("foot_traffic", ""),
                    rent_level=info.get("rent_level", "")
                )
                items.append(region_data.to_dynamodb_item(self.environment))
        
        return items
    
    def _convert_business_types_to_dynamodb_items(self, business_types_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """business_types.json 구조를 DynamoDB 아이템으로 변환"""
        items = []
        
        for business_type, info in business_types_data.items():
            business_data = BusinessTypeData(
                business_type=business_type,
                keywords=info.get("keywords", []),
                typical_size=info.get("typical_size", [0, 0]),
                style_suggestions=info.get("style_suggestions", [])
            )
            items.append(business_data.to_dynamodb_item(self.environment))
        
        return items
    
    def _batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> int:
        """배치로 아이템들을 DynamoDB에 삽입"""
        try:
            # 저장소별 구현에 위임
            if hasattr(self.storage, '_batch_write_items'):
                return self.storage._batch_write_items(table_name, items)
            
            # 폴백: 개별 삽입
            success_count = 0
            for item in items:
                try:
                    # 개별 삽입 로직은 각 저장소에서 구현
                    if hasattr(self.storage, '_put_item'):
                        if self.storage._put_item(table_name, item):
                            success_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to insert item: {str(e)}")
                    continue
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"Batch write failed: {str(e)}")
            return 0
    
    def get_fallback_regions(self) -> Dict[str, Any]:
        """DynamoDB 실패 시 JSON 파일에서 지역 데이터 조회"""
        try:
            regions_file = os.path.join(self.data_dir, "regions.json")
            if os.path.exists(regions_file):
                with open(regions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load fallback regions data: {str(e)}")
        
        return {}
    
    def get_fallback_business_types(self) -> Dict[str, Any]:
        """DynamoDB 실패 시 JSON 파일에서 업종 데이터 조회"""
        try:
            business_types_file = os.path.join(self.data_dir, "business_types.json")
            if os.path.exists(business_types_file):
                with open(business_types_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load fallback business types data: {str(e)}")
        
        return {}