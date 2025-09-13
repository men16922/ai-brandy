"""
LangChain 설정 및 초기화 모듈
환경별 LLM 모델 설정, 체인 캐싱, 콜백 핸들러 등을 관리
"""

import os
from typing import Dict, Any, Optional, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


class ProgressCallbackHandler(BaseCallbackHandler):
    """LangChain 체인 실행 진행 상황을 추적하는 콜백 핸들러 (구조화된 로깅 통합)"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.chain_start_time = None
        self.step_count = 0
        # 구조화된 로거 사용
        from utils.logger import get_logger
        self.logger = get_logger("langchain", os.getenv("APP_ENV", "local"))
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """체인 시작 시 호출"""
        import time
        self.chain_start_time = time.time()
        self.step_count = 0
        chain_name = serialized.get('name', 'Unknown')
        
        self.logger.log_langchain_chain(
            chain_name=chain_name,
            chain_type="chain",
            input_data=inputs,
            success=True,
            session_id=self.session_id,
            status="started"
        )
        
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """체인 종료 시 호출"""
        import time
        if self.chain_start_time:
            duration = time.time() - self.chain_start_time
            self.logger.log_langchain_chain(
                chain_name="chain",
                chain_type="chain",
                input_data={},
                output_data=outputs,
                duration=duration,
                success=True,
                session_id=self.session_id,
                status="completed"
            )
            
    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """체인 오류 시 호출"""
        import time
        duration = None
        if self.chain_start_time:
            duration = time.time() - self.chain_start_time
            
        self.logger.log_langchain_chain(
            chain_name="chain",
            chain_type="chain",
            input_data={},
            duration=duration,
            success=False,
            session_id=self.session_id,
            error=str(error),
            status="failed"
        )
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """LLM 호출 시작 시 호출"""
        self.step_count += 1
        model_name = serialized.get('name', 'Unknown')
        
        self.logger.debug(f"LLM call {self.step_count} started", 
                         session_id=self.session_id, 
                         model=model_name,
                         prompt_count=len(prompts))
        
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """LLM 호출 종료 시 호출"""
        self.logger.debug(f"LLM call {self.step_count} completed", 
                         session_id=self.session_id,
                         generations_count=len(response.generations) if response.generations else 0)


class LangChainConfig:
    """LangChain 설정 관리 클래스"""
    
    def __init__(self, environment: str = None):
        """
        LangChain 설정 초기화
        
        Args:
            environment: 환경 설정 (local/dev)
        """
        self.environment = environment or os.getenv("APP_ENV", "local")
        self.setup_cache()
        self.setup_tracing()
        
    def setup_cache(self):
        """LangChain 캐싱 설정"""
        if os.getenv("ENABLE_CHAIN_CACHING", "true").lower() == "true":
            set_llm_cache(InMemoryCache())
            logger.info("LangChain in-memory cache enabled")
            
    def setup_tracing(self):
        """LangSmith 추적 설정 (선택사항)"""
        if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
            logger.info("LangSmith tracing enabled")
            
    def get_text_llm(self, model_name: str = None, temperature: float = 0.7) -> ChatOpenAI:
        """
        텍스트 생성용 LLM 반환
        
        Args:
            model_name: 모델명 (None이면 환경별 기본값 사용)
            temperature: 창의성 수준 (0.0-1.0)
        """
        if not model_name:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            timeout=int(os.getenv("CHAIN_TIMEOUT_SECONDS", "30")),
            max_retries=3,
            streaming=False
        )
        
    def get_image_llm_openai(self) -> ChatOpenAI:
        """DALL-E 이미지 생성용 LLM 반환"""
        return ChatOpenAI(
            model="gpt-4o",  # DALL-E 프롬프트 생성용
            temperature=0.8,
            timeout=int(os.getenv("CHAIN_TIMEOUT_SECONDS", "30")),
            max_retries=3
        )
        
    def get_image_llm_bedrock(self) -> Optional[ChatBedrock]:
        """AWS Bedrock SDXL용 LLM 반환"""
        try:
            return ChatBedrock(
                model_id="stability.stable-diffusion-xl-v1",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                model_kwargs={
                    "max_tokens": 1000,
                    "temperature": 0.8
                }
            )
        except Exception as e:
            logger.warning(f"Bedrock LLM 초기화 실패: {e}")
            return None
            
    def get_image_llm_gemini(self) -> Optional[ChatGoogleGenerativeAI]:
        """Google Gemini 이미지 생성용 LLM 반환"""
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.8,
                timeout=int(os.getenv("CHAIN_TIMEOUT_SECONDS", "30")),
                max_retries=3
            )
        except Exception as e:
            logger.warning(f"Gemini LLM 초기화 실패: {e}")
            return None
            
    def get_callback_handler(self, session_id: str = None) -> ProgressCallbackHandler:
        """진행 상황 추적용 콜백 핸들러 반환"""
        return ProgressCallbackHandler(session_id)
        
    def get_chain_config(self) -> Dict[str, Any]:
        """체인 실행용 기본 설정 반환"""
        return {
            "max_concurrency": int(os.getenv("MAX_CONCURRENT_CHAINS", "3")),
            "timeout": int(os.getenv("CHAIN_TIMEOUT_SECONDS", "30")),
            "verbose": os.getenv("VERBOSE_LOGGING", "false").lower() == "true",
            "return_intermediate_steps": os.getenv("DEBUG_MODE", "false").lower() == "true"
        }
        
    def validate_api_keys(self) -> Dict[str, bool]:
        """필수 API 키 존재 여부 확인"""
        api_keys = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
            "aws": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")),
            "langsmith": bool(os.getenv("LANGCHAIN_API_KEY")) if os.getenv("LANGCHAIN_TRACING_V2") == "true" else True
        }
        
        missing_keys = [key for key, exists in api_keys.items() if not exists]
        if missing_keys:
            logger.warning(f"Missing API keys: {missing_keys}")
            
        return api_keys


# 전역 설정 인스턴스
_config_instance = None


def get_langchain_config(environment: str = None) -> LangChainConfig:
    """LangChain 설정 싱글톤 인스턴스 반환"""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = LangChainConfig(environment)
        
    return _config_instance


def initialize_langchain(environment: str = None) -> bool:
    """
    LangChain 초기화 및 설정 검증
    
    Args:
        environment: 환경 설정
        
    Returns:
        초기화 성공 여부
    """
    try:
        config = get_langchain_config(environment)
        api_keys = config.validate_api_keys()
        
        # 필수 API 키 확인
        if not api_keys["openai"]:
            logger.error("OpenAI API key is required")
            return False
            
        logger.info(f"LangChain initialized for {config.environment} environment")
        logger.info(f"Available APIs: {[k for k, v in api_keys.items() if v]}")
        
        return True
        
    except Exception as e:
        logger.error(f"LangChain initialization failed: {e}")
        return False


# 사용 예시
if __name__ == "__main__":
    # 환경 변수 로드 (실제 사용 시에는 dotenv 사용)
    import os
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["APP_ENV"] = "local"
    
    # LangChain 초기화
    if initialize_langchain():
        config = get_langchain_config()
        
        # 텍스트 LLM 테스트
        text_llm = config.get_text_llm()
        print(f"Text LLM: {text_llm.model_name}")
        
        # 설정 정보 출력
        chain_config = config.get_chain_config()
        print(f"Chain config: {chain_config}")
        
        # API 키 상태 확인
        api_status = config.validate_api_keys()
        print(f"API keys status: {api_status}")
    else:
        print("LangChain initialization failed")