"""
AI 브랜딩 챗봇 메인 애플리케이션
Streamlit 기반 5단계 워크플로 UI
"""

import streamlit as st
import os
from config.app_config import get_app_config
from config.langchain_config import initialize_langchain
from storage.startup_initializer import initialize_app


def main():
    """메인 애플리케이션 진입점"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="AI 브랜딩 챗봇",
        page_icon="🏪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 설정 초기화
    app_config = get_app_config()
    langchain_initialized = initialize_langchain(app_config.environment)
    
    # 애플리케이션 초기화 (테이블 생성 및 데이터 로드)
    if 'app_initialized' not in st.session_state:
        with st.spinner("애플리케이션 초기화 중..."):
            initialization_success = initialize_app(app_config.environment)
            st.session_state.app_initialized = initialization_success
            if not initialization_success:
                st.error("⚠️ 애플리케이션 초기화에 실패했습니다. 관리자에게 문의하세요.")
                st.stop()
    
    # 헤더
    st.title("🏪 AI 브랜딩 챗봇")
    st.markdown("상호명부터 인테리어까지, AI가 제안하는 완벽한 브랜딩 솔루션")
    
    # 환경 정보 표시 (개발용)
    if app_config.debug_mode:
        with st.sidebar:
            st.info(f"환경: {app_config.environment.upper()}")
            vector_config = app_config.get_vector_store_config()
            st.info(f"벡터 DB: {vector_config['type']}")
            storage_config = app_config.get_storage_config()
            st.info(f"저장소: {storage_config['type']}")
    
    # 헬스체크 엔드포인트 (간단한 방법)
    # 사이드바에 헬스체크 버튼 추가
    with st.sidebar:
        if st.button("🔍 헬스체크"):
            st.success("✅ 애플리케이션이 정상 동작 중입니다.")
            st.info(f"Streamlit 버전: {st.__version__}")
            st.info(f"환경: {app_config.environment}")
            st.info(f"LangChain 초기화: {'성공' if langchain_initialized else '실패'}")
            st.info(f"설정 로드: 성공")
    
    # 임시 메시지 (실제 구현은 다음 태스크에서)
    st.info("🚧 프로젝트 구조가 설정되었습니다. 다음 단계에서 기능을 구현합니다.")
    
    # 환경 설정 확인
    st.subheader("환경 설정 확인")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**디렉토리 구조:**")
        directories = ["config", "data", "logs", "reports", "docker"]
        for directory in directories:
            if os.path.exists(directory):
                st.success(f"✅ {directory}/")
            else:
                st.error(f"❌ {directory}/")
    
    with col2:
        st.write("**설정 파일:**")
        config_files = [".env.local", ".env.dev", "requirements.txt", "docker-compose.yml"]
        for file in config_files:
            if os.path.exists(file):
                st.success(f"✅ {file}")
            else:
                st.error(f"❌ {file}")


if __name__ == "__main__":
    main()