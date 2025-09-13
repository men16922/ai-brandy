"""
DynamoDB 테이블 스키마 로더
JSON 파일에서 테이블 정의를 읽어와서 테이블을 생성
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging


class DynamoDBSchemaLoader:
    """DynamoDB 테이블 스키마 로더"""
    
    def __init__(self, dynamodb_resource, environment: str = "local"):
        """
        스키마 로더 초기화
        
        Args:
            dynamodb_resource: boto3 DynamoDB 리소스
            environment: 환경 설정 (local/dev)
        """
        self.dynamodb = dynamodb_resource
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self.is_local = environment == "local"
        
        # 스키마 파일 경로
        self.schema_dir = Path(__file__).parent / "schemas"
        self.schema_file = self.schema_dir / "dynamodb_tables.json"
    
    def load_table_schemas(self) -> Dict[str, Any]:
        """테이블 스키마 정의 로드"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schemas = json.load(f)
            
            self.logger.info(f"Loaded {len(schemas)} table schemas from {self.schema_file}")
            return schemas
            
        except FileNotFoundError:
            self.logger.error(f"Schema file not found: {self.schema_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in schema file: {e}")
            raise
    
    def get_table_name(self, table_key: str, schema: Dict[str, Any]) -> str:
        """환경에 맞는 테이블명 생성"""
        template = schema.get("table_name_template", f"brandy-{table_key}-{{environment}}")
        return template.format(environment=self.environment)
    
    def create_all_tables(self) -> Dict[str, str]:
        """모든 테이블 생성 (Local 환경에서만)"""
        if not self.is_local:
            raise Exception("Table creation is only supported in local environment. Use CloudFormation for AWS environments.")
        
        schemas = self.load_table_schemas()
        created_tables = {}
        
        for table_key, schema in schemas.items():
            try:
                table_name = self.create_table_from_schema(table_key, schema)
                created_tables[table_key] = table_name
                self.logger.info(f"Successfully created/verified table: {table_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to create table {table_key}: {str(e)}")
                raise
        
        return created_tables
    
    def create_table_from_schema(self, table_key: str, schema: Dict[str, Any]) -> str:
        """스키마 정의에서 테이블 생성"""
        table_name = self.get_table_name(table_key, schema)
        
        # 테이블이 이미 존재하는지 확인
        if self._table_exists(table_name):
            self.logger.info(f"Table {table_name} already exists")
            return table_name
        
        # 테이블 생성 설정 구성
        table_config = {
            'TableName': table_name,
            'KeySchema': schema['key_schema'],
            'AttributeDefinitions': schema['attribute_definitions'],
            'BillingMode': schema.get('billing_mode', 'PAY_PER_REQUEST')
        }
        
        # GSI 추가
        if 'global_secondary_indexes' in schema:
            table_config['GlobalSecondaryIndexes'] = schema['global_secondary_indexes']
        
        # AWS 환경에서는 보안 설정 추가
        if not self.is_local:
            table_config.update({
                'SSESpecification': {
                    'Enabled': True,
                    'SSEType': 'KMS'
                },
                'PointInTimeRecoverySpecification': {
                    'PointInTimeRecoveryEnabled': True
                }
            })
        
        # 테이블 생성
        self.dynamodb.create_table(**table_config)
        self.logger.info(f"Created table: {table_name}")
        
        # 테이블 활성화 대기
        self._wait_for_table_active(table_name)
        
        # TTL 설정 (AWS 환경에서만)
        if not self.is_local and 'ttl_attribute' in schema:
            self._enable_ttl(table_name, schema['ttl_attribute'])
        
        return table_name
    
    def _table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        try:
            table = self.dynamodb.Table(table_name)
            table.load()
            return True
        except Exception:
            return False
    
    def _wait_for_table_active(self, table_name: str, max_wait_time: int = 300):
        """테이블이 활성화될 때까지 대기"""
        start_time = time.time()
        wait_interval = 2 if self.is_local else 5
        
        while time.time() - start_time < max_wait_time:
            try:
                table = self.dynamodb.Table(table_name)
                table.load()
                if table.table_status == 'ACTIVE':
                    self.logger.info(f"Table {table_name} is now active")
                    return
                time.sleep(wait_interval)
            except Exception:
                time.sleep(wait_interval)
        
        raise Exception(f"Table {table_name} did not become active within {max_wait_time} seconds")
    
    def _enable_ttl(self, table_name: str, ttl_attribute: str):
        """TTL 설정 활성화"""
        try:
            table = self.dynamodb.Table(table_name)
            table.meta.client.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    'AttributeName': ttl_attribute,
                    'Enabled': True
                }
            )
            self.logger.info(f"TTL enabled for {table_name} on attribute {ttl_attribute}")
        except Exception as e:
            self.logger.warning(f"Failed to enable TTL for {table_name}: {str(e)}")
    
    def get_table_names(self) -> Dict[str, str]:
        """모든 테이블명 반환"""
        schemas = self.load_table_schemas()
        table_names = {}
        
        for table_key, schema in schemas.items():
            table_names[table_key] = self.get_table_name(table_key, schema)
        
        return table_names
    
    def validate_schemas(self) -> List[str]:
        """스키마 유효성 검증"""
        errors = []
        
        try:
            schemas = self.load_table_schemas()
            
            for table_key, schema in schemas.items():
                # 필수 필드 검증
                required_fields = ['key_schema', 'attribute_definitions']
                for field in required_fields:
                    if field not in schema:
                        errors.append(f"Table {table_key}: Missing required field '{field}'")
                
                # KeySchema 검증
                if 'key_schema' in schema:
                    key_attrs = {item['AttributeName'] for item in schema['key_schema']}
                    defined_attrs = {item['AttributeName'] for item in schema.get('attribute_definitions', [])}
                    
                    missing_attrs = key_attrs - defined_attrs
                    if missing_attrs:
                        errors.append(f"Table {table_key}: Key attributes {missing_attrs} not defined in attribute_definitions")
                
                # GSI 검증
                if 'global_secondary_indexes' in schema:
                    for gsi in schema['global_secondary_indexes']:
                        if 'IndexName' not in gsi:
                            errors.append(f"Table {table_key}: GSI missing IndexName")
                        
                        if 'KeySchema' in gsi:
                            gsi_attrs = {item['AttributeName'] for item in gsi['KeySchema']}
                            defined_attrs = {item['AttributeName'] for item in schema.get('attribute_definitions', [])}
                            
                            missing_attrs = gsi_attrs - defined_attrs
                            if missing_attrs:
                                errors.append(f"Table {table_key}: GSI attributes {missing_attrs} not defined in attribute_definitions")
        
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
        
        return errors


# 편의 함수
def create_tables_from_schema(dynamodb_resource, environment: str = "local") -> Dict[str, str]:
    """스키마 파일에서 모든 테이블 생성"""
    loader = DynamoDBSchemaLoader(dynamodb_resource, environment)
    return loader.create_all_tables()


def get_table_names_from_schema(environment: str = "local") -> Dict[str, str]:
    """스키마 파일에서 테이블명 목록 반환"""
    # DynamoDB 리소스 없이도 테이블명은 가져올 수 있음
    loader = DynamoDBSchemaLoader(None, environment)
    return loader.get_table_names()


def validate_table_schemas() -> List[str]:
    """테이블 스키마 유효성 검증"""
    loader = DynamoDBSchemaLoader(None)
    return loader.validate_schemas()


if __name__ == "__main__":
    # 스키마 검증 실행
    errors = validate_table_schemas()
    if errors:
        print("Schema validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("All schemas are valid!")