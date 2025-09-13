"""
구조화된 로깅 시스템
환경별 로그 레벨 설정 및 로그 파일 로테이션 지원
"""

import logging
import logging.handlers
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredLogger:
    """구조화된 로깅을 위한 클래스"""
    
    def __init__(self, name: str, environment: str = "local"):
        """
        로거 초기화
        
        Args:
            name: 로거 이름
            environment: 환경 (local: DEBUG, dev: INFO)
        """
        self.name = name
        self.environment = environment
        self.logger = logging.getLogger(name)
        
        # 환경별 로그 레벨 설정
        if environment == "local":
            self.log_level = logging.DEBUG
        else:  # dev 환경
            self.log_level = logging.INFO
            
        self.logger.setLevel(self.log_level)
        
        # 중복 핸들러 방지
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """로그 핸들러 설정"""
        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 파일 핸들러 (로테이션 지원)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / f"{self.name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # 최대 5개 백업 파일
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # JSON 형태의 구조화된 로그 포맷터
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def _create_log_entry(self, level: str, message: str, **kwargs) -> str:
        """구조화된 로그 엔트리 생성"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "environment": self.environment,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry, ensure_ascii=False)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        if self.logger.isEnabledFor(logging.DEBUG):
            log_entry = self._create_log_entry("DEBUG", message, **kwargs)
            self.logger.debug(log_entry)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        log_entry = self._create_log_entry("INFO", message, **kwargs)
        self.logger.info(log_entry)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        log_entry = self._create_log_entry("WARNING", message, **kwargs)
        self.logger.warning(log_entry)
    
    def error(self, message: str, **kwargs):
        """오류 로그"""
        log_entry = self._create_log_entry("ERROR", message, **kwargs)
        self.logger.error(log_entry)
    
    def critical(self, message: str, **kwargs):
        """치명적 오류 로그"""
        log_entry = self._create_log_entry("CRITICAL", message, **kwargs)
        self.logger.critical(log_entry)
    
    def log_api_call(self, endpoint: str, method: str = "POST", 
                     duration: Optional[float] = None, status: str = "success", 
                     **kwargs):
        """
        API 호출 로깅
        
        Args:
            endpoint: API 엔드포인트
            method: HTTP 메서드
            duration: 응답 시간 (초)
            status: 호출 상태 (success/error)
            **kwargs: 추가 메타데이터
        """
        log_data = {
            "event_type": "api_call",
            "endpoint": endpoint,
            "method": method,
            "status": status,
            **kwargs
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"API call to {endpoint} - {status}"
        if duration:
            message += f" ({duration:.3f}s)"
            
        if status == "success":
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, 
                  operation: Optional[str] = None):
        """
        오류 로깅
        
        Args:
            error: 발생한 예외
            context: 오류 발생 컨텍스트
            operation: 수행 중이던 작업
        """
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        
        if context:
            log_data["context"] = context
            
        if operation:
            log_data["operation"] = operation
            
        message = f"Error in {operation or 'unknown operation'}: {str(error)}"
        self.error(message, **log_data)
    
    def log_performance(self, operation: str, duration: float, 
                       success: bool = True, **kwargs):
        """
        성능 메트릭 로깅
        
        Args:
            operation: 수행된 작업
            duration: 소요 시간 (초)
            success: 성공 여부
            **kwargs: 추가 메트릭
        """
        log_data = {
            "event_type": "performance",
            "operation": operation,
            "duration_seconds": round(duration, 3),
            "success": success,
            **kwargs
        }
        
        message = f"Performance: {operation} completed in {duration:.3f}s"
        if not success:
            message += " (failed)"
            
        if success:
            self.info(message, **log_data)
        else:
            self.warning(message, **log_data)
    
    def log_workflow_step(self, session_id: str, step: int, action: str, 
                         duration: Optional[float] = None, **kwargs):
        """
        워크플로 단계 로깅
        
        Args:
            session_id: 세션 ID
            step: 워크플로 단계 (1-5)
            action: 수행된 액션
            duration: 소요 시간
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "workflow",
            "session_id": session_id,
            "step": step,
            "action": action,
            **kwargs
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"Workflow Step {step}: {action} for session {session_id[:8]}"
        if duration:
            message += f" ({duration:.3f}s)"
            
        self.info(message, **log_data)
    
    def log_image_generation(self, model: str, prompt: str, success: bool, 
                           duration: Optional[float] = None, **kwargs):
        """
        이미지 생성 로깅
        
        Args:
            model: 사용된 AI 모델
            prompt: 생성 프롬프트
            success: 성공 여부
            duration: 소요 시간
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "image_generation",
            "model": model,
            "prompt_length": len(prompt),
            "success": success,
            **kwargs
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"Image generation with {model} - {'success' if success else 'failed'}"
        if duration:
            message += f" ({duration:.3f}s)"
            
        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_langchain_chain(self, chain_name: str, chain_type: str, 
                           input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None,
                           duration: Optional[float] = None, success: bool = True, **kwargs):
        """
        LangChain 체인 실행 로깅
        
        Args:
            chain_name: 체인 이름
            chain_type: 체인 타입 (text, image, rag 등)
            input_data: 입력 데이터
            output_data: 출력 데이터 (선택사항)
            duration: 소요 시간
            success: 성공 여부
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "langchain_chain",
            "chain_name": chain_name,
            "chain_type": chain_type,
            "input_size": len(str(input_data)) if input_data else 0,
            "success": success,
            **kwargs
        }
        
        if output_data:
            log_data["output_size"] = len(str(output_data))
            
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"LangChain {chain_type} chain '{chain_name}' - {'success' if success else 'failed'}"
        if duration:
            message += f" ({duration:.3f}s)"
            
        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_rag_query(self, query: str, knowledge_base: str, results_count: int,
                     duration: Optional[float] = None, success: bool = True, **kwargs):
        """
        RAG 검색 쿼리 로깅
        
        Args:
            query: 검색 쿼리
            knowledge_base: 지식베이스 이름 (chroma, bedrock 등)
            results_count: 검색 결과 개수
            duration: 소요 시간
            success: 성공 여부
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "rag_query",
            "knowledge_base": knowledge_base,
            "query_length": len(query),
            "results_count": results_count,
            "success": success,
            **kwargs
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"RAG query on {knowledge_base} - {results_count} results"
        if duration:
            message += f" ({duration:.3f}s)"
            
        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_storage_operation(self, operation: str, storage_type: str, 
                             object_key: str, success: bool = True,
                             duration: Optional[float] = None, **kwargs):
        """
        저장소 작업 로깅 (MinIO, S3, DynamoDB)
        
        Args:
            operation: 작업 타입 (get, put, delete, query 등)
            storage_type: 저장소 타입 (minio, s3, dynamodb)
            object_key: 객체 키 또는 테이블명
            success: 성공 여부
            duration: 소요 시간
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "storage_operation",
            "operation": operation,
            "storage_type": storage_type,
            "object_key": object_key,
            "success": success,
            **kwargs
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
            
        message = f"Storage {operation} on {storage_type}:{object_key} - {'success' if success else 'failed'}"
        if duration:
            message += f" ({duration:.3f}s)"
            
        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)


class LoggerFactory:
    """로거 팩토리 클래스"""
    
    _loggers: Dict[str, StructuredLogger] = {}
    
    @classmethod
    def get_logger(cls, name: str, environment: str = None) -> StructuredLogger:
        """
        로거 인스턴스 반환 (싱글톤 패턴)
        
        Args:
            name: 로거 이름
            environment: 환경 설정 (None이면 환경변수에서 읽음)
        """
        if environment is None:
            environment = os.getenv("APP_ENV", "local")
            
        logger_key = f"{name}_{environment}"
        
        if logger_key not in cls._loggers:
            cls._loggers[logger_key] = StructuredLogger(name, environment)
            
        return cls._loggers[logger_key]


# 편의를 위한 전역 함수들
def get_logger(name: str, environment: str = None) -> StructuredLogger:
    """로거 인스턴스 반환"""
    return LoggerFactory.get_logger(name, environment)


# 성능 측정을 위한 컨텍스트 매니저
class LoggedOperation:
    """성능 로깅을 위한 컨텍스트 매니저"""
    
    def __init__(self, logger: StructuredLogger, operation: str, **kwargs):
        self.logger = logger
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.success = False
            self.logger.log_error(exc_val, operation=self.operation)
        
        self.logger.log_performance(
            self.operation, 
            duration, 
            self.success, 
            **self.kwargs
        )
        
        return False  # 예외를 다시 발생시킴


# LangChain 통합 콜백 핸들러
class LangChainLoggingHandler:
    """LangChain 체인 실행을 로깅하는 핸들러"""
    
    def __init__(self, logger: StructuredLogger, session_id: str = None):
        self.logger = logger
        self.session_id = session_id
        self.chain_start_time = None
        self.chain_name = None
        
    def on_chain_start(self, chain_name: str, inputs: Dict[str, Any]):
        """체인 시작 시 호출"""
        self.chain_start_time = time.time()
        self.chain_name = chain_name
        self.logger.debug(f"Starting LangChain: {chain_name}", 
                         session_id=self.session_id, inputs_size=len(str(inputs)))
        
    def on_chain_end(self, outputs: Dict[str, Any]):
        """체인 종료 시 호출"""
        if self.chain_start_time and self.chain_name:
            duration = time.time() - self.chain_start_time
            self.logger.log_langchain_chain(
                chain_name=self.chain_name,
                chain_type="unknown",
                input_data={},
                output_data=outputs,
                duration=duration,
                success=True,
                session_id=self.session_id
            )
            
    def on_chain_error(self, error: Exception):
        """체인 오류 시 호출"""
        if self.chain_start_time and self.chain_name:
            duration = time.time() - self.chain_start_time
            self.logger.log_langchain_chain(
                chain_name=self.chain_name,
                chain_type="unknown",
                input_data={},
                duration=duration,
                success=False,
                session_id=self.session_id,
                error=str(error)
            )


# 사용 예시
if __name__ == "__main__":
    # 로거 생성
    logger = get_logger("test", "local")
    
    # 기본 로깅
    logger.info("Application started")
    logger.debug("Debug information", user_id="12345")
    
    # API 호출 로깅
    logger.log_api_call(
        endpoint="/api/generate-names",
        duration=2.5,
        status="success",
        response_size=1024
    )
    
    # 오류 로깅
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error(e, context={"user_id": "12345"}, operation="test_operation")
    
    # 성능 로깅
    logger.log_performance("image_generation", 15.2, success=True, model="DALL-E")
    
    # LangChain 체인 로깅
    logger.log_langchain_chain(
        chain_name="business_name_generator",
        chain_type="text",
        input_data={"business_type": "카페", "location": "강남"},
        output_data={"names": ["카페 모던", "브라운 커피", "심플 카페"]},
        duration=3.2,
        success=True
    )
    
    # RAG 쿼리 로깅
    logger.log_rag_query(
        query="카페 인테리어 트렌드",
        knowledge_base="chroma",
        results_count=5,
        duration=1.8,
        success=True
    )
    
    # 저장소 작업 로깅
    logger.log_storage_operation(
        operation="put",
        storage_type="minio",
        object_key="images/cafe_sign_001.jpg",
        success=True,
        duration=0.5,
        file_size=1024000
    )
    
    # 컨텍스트 매니저 사용
    with LoggedOperation(logger, "complex_operation", user_id="12345"):
        time.sleep(1)  # 시뮬레이션
        logger.info("Operation completed")