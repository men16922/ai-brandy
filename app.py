"""
AI 브랜딩 챗봇 메인 애플리케이션
Streamlit 기반 5단계 워크플로 UI
"""

import streamlit as st
import os
from typing import Dict, Any

from config.app_config import get_app_config
from config.langchain_config import initialize_langchain
from storage.startup_initializer import initialize_app
from storage.storage_factory import StorageManager


def initialize_application() -> bool:
    """애플리케이션 초기화"""
    if 'app_initialized' not in st.session_state:
        app_config = get_app_config()
        
        with st.spinner("애플리케이션 초기화 중..."):
            # LangChain 초기화
            langchain_success = initialize_langchain(app_config.environment)
            
            # 저장소 및 데이터 초기화
            storage_success = initialize_app(app_config.environment)
            
            success = langchain_success and storage_success
            st.session_state.app_initialized = success
            st.session_state.langchain_initialized = langchain_success
            
            if not success:
                st.error("⚠️ 애플리케이션 초기화에 실패했습니다. 관리자에게 문의하세요.")
                return False
    
    return st.session_state.get('app_initialized', False)


def render_sidebar() -> None:
    """사이드바 렌더링"""
    app_config = get_app_config()
    
    with st.sidebar:
        st.header("🔧 시스템 정보")
        
        # 환경 정보
        st.info(f"**환경**: {app_config.environment.upper()}")
        
        # 디버그 모드에서 추가 정보 표시
        if app_config.debug_mode:
            vector_config = app_config.get_vector_store_config()
            storage_config = app_config.get_storage_config()
            st.info(f"**벡터 DB**: {vector_config['type']}")
            st.info(f"**저장소**: {storage_config['type']}")
        
        # 헬스체크
        if st.button("🔍 헬스체크", use_container_width=True):
            perform_health_check()


def perform_health_check() -> None:
    """헬스체크 수행"""
    app_config = get_app_config()
    
    st.success("✅ 애플리케이션이 정상 동작 중입니다.")
    
    # 기본 정보
    st.info(f"**Streamlit**: {st.__version__}")
    st.info(f"**환경**: {app_config.environment}")
    st.info(f"**LangChain**: {'✅ 성공' if st.session_state.get('langchain_initialized') else '❌ 실패'}")
    
    # 저장소 헬스체크
    try:
        storage_manager = StorageManager()
        storage = storage_manager.get_storage(app_config.environment)
        health_results = storage.health_check()
        
        st.write("**저장소 상태:**")
        for result in health_results:
            status_icon = "✅" if result.status == "healthy" else "❌"
            st.info(f"{status_icon} **{result.service_name}**: {result.message}")
            
    except Exception as e:
        st.error(f"❌ 저장소 헬스체크 실패: {str(e)}")


def render_main_content() -> None:
    """메인 콘텐츠 렌더링"""
    # 헤더
    st.title("🏪 AI 브랜딩 챗봇")
    st.markdown("상호명부터 인테리어까지, AI가 제안하는 완벽한 브랜딩 솔루션")
    
    # 현재 상태 표시
    st.info("🚧 프로젝트 구조가 설정되었습니다. 5단계 워크플로 UI를 구현할 준비가 완료되었습니다.")
    
    # 워크플로 단계 미리보기
    st.subheader("📋 5단계 워크플로")
    
    steps = [
        ("1️⃣", "비즈니스 정보 입력", "업종, 지역, 평수 등 기본 정보 수집"),
        ("2️⃣", "상호명 생성", "AI가 추천하는 3개의 상호명 (재생성 최대 3회)"),
        ("3️⃣", "간판 디자인", "선택된 상호명으로 3가지 간판 디자인 생성"),
        ("4️⃣", "인테리어 추천", "간판과 조화를 맞춘 3가지 인테리어 디자인"),
        ("5️⃣", "PDF 보고서", "최종 선택사항을 포함한 완성된 보고서 생성")
    ]
    
    for icon, title, description in steps:
        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.markdown(f"### {icon}")
            with col2:
                st.markdown(f"**{title}**")
                st.markdown(description)
            st.divider()


def main():
    """메인 애플리케이션 진입점"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="AI 브랜딩 챗봇",
        page_icon="🏪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 애플리케이션 초기화
    if not initialize_application():
        st.stop()
    
    # UI 렌더링
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()