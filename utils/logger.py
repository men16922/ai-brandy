"""
로깅 시스템
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any

class Logger:
    """구조화된 로거"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 핸들러가 이미 있으면 추가하지 않음
        if not self.logger.handlers:
            # 콘솔 핸들러
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, level.upper()))
            
            # 포매터
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """정보 로그"""
        if context:
            message = f"{message} | Context: {context}"
        self.logger.info(message)
    
    def error(self, message: str, error: Exception = None, context: Dict[str, Any] = None):
        """오류 로그"""
        if error:
            message = f"{message} | Error: {str(error)}"
        if context:
            message = f"{message} | Context: {context}"
        self.logger.error(message)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """경고 로그"""
        if context:
            message = f"{message} | Context: {context}"
        self.logger.warning(message)
    
    def debug(self, message: str, context: Dict[str, Any] = None):
        """디버그 로그"""
        if context:
            message = f"{message} | Context: {context}"
        self.logger.debug(message)

# 전역 로거 인스턴스
logger = Logger("ai-branding-chatbot")