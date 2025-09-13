"""
애플리케이션 시작 시 자동 초기화
테이블 생성 및 JSON 데이터 마이그레이션을 자동으로 수행
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경변수 로드 (환경에 따라 적절한 .env 파일 로드)
# 주의: 이미 환경변수가 설정된 경우 덮어쓰지 않음

from storage.storage_factory import StorageManager
from storage.data_initializer import DataInitializer


class StartupInitializer:
    """애플리케이션 시작 시 자동 초기화 클래스"""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv('APP_ENV', 'local')
        self.logger = logging.getLogger(__name__)
        
        # 환경에 맞는 .env 파일 로드 (이미 설정된 환경변수는 덮어쓰지 않음)
        env_file = f'.env.{self.environment}'
        if os.path.exists(env_file):
            load_dotenv(env_file, override=False)
            self.logger.info(f"Loaded environment file: {env_file}")
        else:
            self.logger.warning(f"Environment file not found: {env_file}")
        
    def initialize_application(self) -> bool:
        """애플리케이션 전체 초기화"""
        try:
            self.logger.info(f"Starting application initialization for {self.environment} environment")
            
            # 1. 저장소 매니저 초기화
            manager = StorageManager()
            storage = manager.get_storage(self.environment)
            
            # 2. 테이블 생성 및 초기화
            self.logger.info("Initializing storage tables...")
            if not storage.initialize_tables():
                self.logger.error("Failed to initialize storage tables")
                return False
            
            # 3. 데이터 마이그레이션
            self.logger.info("Starting data migration...")
            data_initializer = DataInitializer(storage, self.environment)
            
            if not data_initializer.initialize_all_data():
                self.logger.warning("Data migration completed with warnings, using fallback data")
            else:
                self.logger.info("Data migration completed successfully")
            
            # 4. 헬스체크 수행
            self.logger.info("Performing health check...")
            health_results = storage.health_check()
            
            healthy_services = 0
            for result in health_results:
                if result.status == "healthy":
                    healthy_services += 1
                    self.logger.info(f"✓ {result.service_name}: {result.message}")
                else:
                    self.logger.warning(f"✗ {result.service_name}: {result.message}")
            
            if healthy_services == 0:
                self.logger.error("No healthy services found!")
                return False
            
            self.logger.info(f"Application initialization completed. {healthy_services}/{len(health_results)} services healthy")
            return True
            
        except Exception as e:
            self.logger.error(f"Application initialization failed: {str(e)}")
            return False
    
    def verify_data_loaded(self) -> bool:
        """데이터가 제대로 로드되었는지 확인"""
        try:
            manager = StorageManager()
            storage = manager.get_storage(self.environment)
            
            # 지역 데이터 확인
            regions = storage.get_regions()
            if not regions:
                self.logger.warning("No regions data found")
                return False
            
            # 업종 데이터 확인
            business_types = storage.get_business_types()
            if not business_types:
                self.logger.warning("No business types data found")
                return False
            
            self.logger.info(f"Data verification successful: {len(regions)} regions, {len(business_types)} business types")
            return True
            
        except Exception as e:
            self.logger.error(f"Data verification failed: {str(e)}")
            return False


def initialize_app(environment: Optional[str] = None) -> bool:
    """애플리케이션 초기화 함수 (외부에서 호출용)"""
    initializer = StartupInitializer(environment)
    return initializer.initialize_application()


if __name__ == "__main__":
    # 직접 실행 시 초기화 수행
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== Application Startup Initialization ===")
    success = initialize_app()
    
    if success:
        print("✓ Application initialization completed successfully!")
        
        # 데이터 검증
        initializer = StartupInitializer()
        if initializer.verify_data_loaded():
            print("✓ Data verification passed!")
        else:
            print("✗ Data verification failed!")
    else:
        print("✗ Application initialization failed!")
        exit(1)