"""
통합 저장소 구현
- Local 환경: MinIO + DynamoDB Local (Python 코드로 리소스 생성)
- AWS 환경: S3 + DynamoDB (CloudFormation으로 생성된 리소스 사용)
"""

import os
import boto3
import time
from typing import Dict, List, Optional, Any
import logging
from botocore.exceptions import ClientError
from models.data_models import HealthCheckResult
from storage.base_storage import BaseStorage
from storage.schema_loader import DynamoDBSchemaLoader


class UnifiedStorage(BaseStorage):
    """통합 저장소 (환경변수 기반 자동 설정)"""
    
    def __init__(self, environment: str = "local"):
        super().__init__(environment)
        self.logger = logging.getLogger(__name__)
        
        # 환경변수에서 설정 읽기
        self._load_config()
        
        # AWS 서비스 클라이언트 초기화
        self._init_dynamodb()
        self._init_s3()
        
        # 스키마 로더 초기화
        self.schema_loader = DynamoDBSchemaLoader(self.dynamodb, self.environment)
        
        # 테이블 이름 설정
        self._setup_table_names()
    
    def _load_config(self):
        """환경변수에서 설정 로드"""
        # DynamoDB 설정
        self.dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT')  # Local에서만 설정됨
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')  # None이면 기본 자격증명 체인 사용
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')  # None이면 기본 자격증명 체인 사용
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # S3 설정 (Local에서는 MinIO, Dev에서는 AWS S3)
        self.s3_endpoint = os.getenv('S3_ENDPOINT')  # Local에서만 설정됨
        self.s3_access_key = os.getenv('S3_ACCESS_KEY', self.aws_access_key)
        self.s3_secret_key = os.getenv('S3_SECRET_KEY', self.aws_secret_key)
        self.bucket_name = os.getenv('S3_BUCKET_NAME', f'ai-branding-{self.environment}')
        
        # 환경 구분
        self.is_local = self.environment == 'local'
        
        self.logger.info(f"Storage config loaded for {self.environment} environment")
        if self.is_local:
            self.logger.info(f"  DynamoDB: {self.dynamodb_endpoint}")
            self.logger.info(f"  S3 (MinIO): {self.s3_endpoint}")
        else:
            self.logger.info(f"  Using AWS services in region: {self.aws_region}")
            self.logger.info(f"  S3 Bucket: {self.bucket_name}")
            self.logger.info(f"  AWS credentials: {'Explicit' if self.aws_access_key else 'Default chain'}")
            if self.aws_access_key:
                self.logger.info(f"  Access Key: {self.aws_access_key[:10]}...")
    
    def _init_dynamodb(self):
        """DynamoDB 클라이언트 초기화"""
        dynamodb_config = {
            'region_name': self.aws_region
        }
        
        # Local 환경에서는 명시적 자격증명과 엔드포인트 사용
        if self.is_local:
            if self.aws_access_key and self.aws_secret_key:
                dynamodb_config.update({
                    'aws_access_key_id': self.aws_access_key,
                    'aws_secret_access_key': self.aws_secret_key
                })
            if self.dynamodb_endpoint:
                dynamodb_config['endpoint_url'] = self.dynamodb_endpoint
        else:
            # AWS 환경에서는 명시적 자격증명이 있으면 사용, 없으면 기본 체인 사용
            if self.aws_access_key and self.aws_secret_key:
                dynamodb_config.update({
                    'aws_access_key_id': self.aws_access_key,
                    'aws_secret_access_key': self.aws_secret_key
                })
        
        self.dynamodb = boto3.resource('dynamodb', **dynamodb_config)
    
    def _init_s3(self):
        """S3 클라이언트 초기화"""
        s3_config = {
            'region_name': self.aws_region
        }
        
        # Local 환경에서는 명시적 자격증명과 MinIO 엔드포인트 사용
        if self.is_local:
            if self.s3_access_key and self.s3_secret_key:
                s3_config.update({
                    'aws_access_key_id': self.s3_access_key,
                    'aws_secret_access_key': self.s3_secret_key
                })
                self.logger.info(f"Using explicit S3 credentials for local environment")
            if self.s3_endpoint:
                s3_config['endpoint_url'] = self.s3_endpoint
        else:
            # AWS 환경에서는 명시적 자격증명이 있으면 사용, 없으면 기본 체인 사용
            if self.s3_access_key and self.s3_secret_key:
                s3_config.update({
                    'aws_access_key_id': self.s3_access_key,
                    'aws_secret_access_key': self.s3_secret_key
                })
                self.logger.info(f"Using explicit S3 credentials: {self.s3_access_key[:10]}...")
            else:
                self.logger.info("Using default AWS credential chain for S3")
        
        self.s3_client = boto3.client('s3', **s3_config)
    
    def _setup_table_names(self):
        """테이블 이름 설정 (스키마에서 로드)"""
        self.table_names = self.schema_loader.get_table_names()
    
    def initialize_tables(self) -> bool:
        """DynamoDB 테이블 및 S3 버킷 초기화"""
        try:
            if self.is_local:
                # Local 환경: Python 코드로 리소스 생성
                self._create_local_resources()
            else:
                # Dev 환경: CloudFormation으로 생성된 리소스 확인
                self._verify_aws_resources()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize resources: {str(e)}")
            return False
    
    def _create_local_resources(self):
        """Local 환경 리소스 생성 (MinIO 버킷 + DynamoDB Local 테이블)"""
        # MinIO 버킷 생성
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"MinIO bucket {self.bucket_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                self.logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                raise
        
        # DynamoDB Local 테이블 생성
        created_tables = self.schema_loader.create_all_tables()
        self.logger.info(f"Initialized {len(created_tables)} local tables: {list(created_tables.values())}")
    
    def _verify_aws_resources(self):
        """AWS 리소스 존재 여부 확인 (CloudFormation으로 생성된 리소스)"""
        try:
            # S3 버킷 확인
            self.logger.info(f"Checking S3 bucket: {self.bucket_name}")
            
            # 더 자세한 S3 클라이언트 정보 출력
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                self.logger.info(f"Using credentials: {credentials.access_key[:10]}... (region: {self.aws_region})")
                self.logger.info(f"Credentials source: {credentials.method if hasattr(credentials, 'method') else 'unknown'}")
            else:
                self.logger.error("No credentials found!")
            
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"✅ S3 bucket verified: {self.bucket_name}")
            
            # DynamoDB 테이블들 확인
            for table_key, table_name in self.table_names.items():
                self.logger.info(f"Checking DynamoDB table: {table_name}")
                table = self.dynamodb.Table(table_name)
                table.load()
                self.logger.info(f"✅ DynamoDB table verified: {table_name}")
            
            self.logger.info("All AWS resources are available (created by CloudFormation)")
            
        except Exception as e:
            self.logger.error(f"AWS resource verification failed: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            
            # S3 버킷 접근 권한 문제인 경우 더 자세한 안내
            if "403" in str(e) or "Forbidden" in str(e):
                error_msg = f"""
❌ S3 버킷 접근 권한이 없습니다: {self.bucket_name}

가능한 원인:
1. AWS 자격증명 문제: 현재 사용자에게 S3 접근 권한이 없음
2. 버킷 정책 문제: 버킷에 접근을 차단하는 정책이 설정됨
3. 리전 불일치: 버킷이 다른 리전에 있음

해결 방법:
1. AWS 자격증명 확인:
   aws sts get-caller-identity
   
2. S3 버킷 접근 테스트:
   aws s3 ls s3://{self.bucket_name}
   
3. CloudFormation 스택 상태 확인:
   aws cloudformation describe-stacks --stack-name brandy-infrastructure-{self.environment}

오류 상세: {str(e)}
"""
            else:
                error_msg = f"""
❌ AWS 리소스를 찾을 수 없습니다. CloudFormation 스택을 배포해주세요:

배포 명령어:
  ./scripts/deploy-infrastructure.sh -e {self.environment}

또는 수동으로:
  aws cloudformation create-stack \\
    --stack-name brandy-infrastructure-{self.environment} \\
    --template-body file://infrastructure/cloudformation/dynamodb-tables.yaml \\
    --parameters ParameterKey=Environment,ParameterValue={self.environment} \\
    --capabilities CAPABILITY_NAMED_IAM

오류 상세: {str(e)}
"""
            
            self.logger.error(error_msg)
            raise Exception(f"AWS resources not found. Please deploy CloudFormation stack first. Error: {str(e)}")
    

    
    def save_chat_history(self, session_id: str, message: Dict[str, Any]) -> bool:
        """채팅 이력 저장"""
        try:
            table = self.dynamodb.Table(self.table_names["workflow"])
            
            table.update_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET chat_history = list_append(if_not_exists(chat_history, :empty_list), :message)',
                ExpressionAttributeValues={
                    ':empty_list': [],
                    ':message': [message]
                },
                ReturnValues='UPDATED_NEW'
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save chat history: {str(e)}")
            return False
    
    def save_image(self, image_data: bytes, key: str) -> str:
        """이미지 저장"""
        try:
            put_object_args = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': image_data,
                'ContentType': 'image/jpeg'
            }
            
            # AWS 환경에서는 암호화 설정
            if not self.is_local:
                put_object_args['ServerSideEncryption'] = 'AES256'
            
            self.s3_client.put_object(**put_object_args)
            
            # URL 생성
            if self.is_local:
                return f"{self.s3_endpoint}/{self.bucket_name}/{key}"
            else:
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            
        except Exception as e:
            self.logger.error(f"Failed to save image: {str(e)}")
            raise
    
    def upload_to_vector_store(self, file_path: str, metadata: Dict[str, Any]) -> str:
        """벡터 스토어에 파일 업로드"""
        try:
            import os
            
            key = f"vector-store/{os.path.basename(file_path)}"
            
            upload_args = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Metadata': {k: str(v) for k, v in metadata.items()}  # 메타데이터는 문자열만 가능
            }
            
            # AWS 환경에서는 암호화 설정
            if not self.is_local:
                upload_args['ServerSideEncryption'] = 'AES256'
            
            with open(file_path, 'rb') as f:
                upload_args['Body'] = f.read()
                self.s3_client.put_object(**upload_args)
            
            # URL 생성
            if self.is_local:
                return f"{self.s3_endpoint}/{self.bucket_name}/{key}"
            else:
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            
        except Exception as e:
            self.logger.error(f"Failed to upload to vector store: {str(e)}")
            raise
    
    def get_regions(self) -> Dict[str, Any]:
        """지역 데이터 조회"""
        try:
            table = self.dynamodb.Table(self.table_names["regions"])
            
            response = table.scan()
            items = response.get('Items', [])
            
            # 페이지네이션 처리 (AWS에서 필요할 수 있음)
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            # DynamoDB 아이템을 원래 JSON 구조로 변환
            regions = {}
            for item in items:
                region = item['region']
                district = item['district']
                
                if region not in regions:
                    regions[region] = {}
                
                regions[region][district] = {
                    'characteristics': item.get('characteristics', []),
                    'foot_traffic': item.get('foot_traffic', ''),
                    'rent_level': item.get('rent_level', '')
                }
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Failed to get regions: {str(e)}")
            return {}
    
    def get_business_types(self) -> Dict[str, Any]:
        """업종 데이터 조회"""
        try:
            table = self.dynamodb.Table(self.table_names["business_types"])
            
            response = table.scan()
            items = response.get('Items', [])
            
            # 페이지네이션 처리
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            # DynamoDB 아이템을 원래 JSON 구조로 변환
            business_types = {}
            for item in items:
                business_type = item['business_type']
                business_types[business_type] = {
                    'keywords': item.get('keywords', []),
                    'typical_size': item.get('typical_size', [0, 0]),
                    'style_suggestions': item.get('style_suggestions', [])
                }
            
            return business_types
            
        except Exception as e:
            self.logger.error(f"Failed to get business types: {str(e)}")
            return {}
    
    def save_workflow_session(self, session_data: Dict[str, Any]) -> bool:
        """워크플로 세션 저장"""
        try:
            table = self.dynamodb.Table(self.table_names["workflow"])
            table.put_item(Item=session_data)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save workflow session: {str(e)}")
            return False
    
    def get_workflow_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """워크플로 세션 조회"""
        try:
            table = self.dynamodb.Table(self.table_names["workflow"])
            
            response = table.get_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'METADATA'
                }
            )
            
            return response.get('Item')
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow session: {str(e)}")
            return None
    
    def update_workflow_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """워크플로 세션 업데이트"""
        try:
            table = self.dynamodb.Table(self.table_names["workflow"])
            
            # 업데이트 표현식 생성
            update_expression = "SET "
            expression_values = {}
            
            for key, value in updates.items():
                update_expression += f"{key} = :{key}, "
                expression_values[f":{key}"] = value
            
            # 마지막 쉼표 제거
            update_expression = update_expression.rstrip(", ")
            
            table.update_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update workflow session: {str(e)}")
            return False
    
    def _check_table_has_data(self, table_name: str) -> bool:
        """테이블에 데이터가 있는지 확인"""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.scan(Limit=1)
            return response['Count'] > 0
        except Exception as e:
            self.logger.warning(f"Could not check data in table {table_name}: {str(e)}")
            return False
    
    def _batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> int:
        """배치로 아이템들을 DynamoDB에 삽입"""
        try:
            table = self.dynamodb.Table(table_name)
            success_count = 0
            
            # DynamoDB batch_writer 사용 (최대 25개씩 처리)
            with table.batch_writer() as batch:
                for item in items:
                    try:
                        batch.put_item(Item=item)
                        success_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to insert item: {str(e)}")
                        continue
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"Batch write failed: {str(e)}")
            return 0
    
    def _put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """개별 아이템을 DynamoDB에 삽입"""
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
            return True
        except Exception as e:
            self.logger.warning(f"Failed to put item: {str(e)}")
            return False

    def health_check(self) -> List[HealthCheckResult]:
        """헬스체크 수행"""
        results = []
        
        # DynamoDB 헬스체크
        start_time = time.time()
        try:
            list(self.dynamodb.tables.all())
            response_time = (time.time() - start_time) * 1000
            
            service_name = "DynamoDB Local" if self.is_local else "AWS DynamoDB"
            results.append(HealthCheckResult(
                service_name=service_name,
                status="healthy",
                message="Connection successful",
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            service_name = "DynamoDB Local" if self.is_local else "AWS DynamoDB"
            results.append(HealthCheckResult(
                service_name=service_name,
                status="unhealthy",
                message=f"Connection failed: {str(e)}",
                response_time_ms=response_time
            ))
        
        # S3 헬스체크
        start_time = time.time()
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            response_time = (time.time() - start_time) * 1000
            
            service_name = "MinIO S3" if self.is_local else "AWS S3"
            results.append(HealthCheckResult(
                service_name=service_name,
                status="healthy",
                message="Bucket accessible",
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            service_name = "MinIO S3" if self.is_local else "AWS S3"
            results.append(HealthCheckResult(
                service_name=service_name,
                status="unhealthy",
                message=f"Bucket access failed: {str(e)}",
                response_time_ms=response_time
            ))
        
        return results
    
