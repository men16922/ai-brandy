#!/usr/bin/env python3
"""
기동 테스트 스크립트
애플리케이션의 기본 기동 가능성을 테스트
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def test_config_loading():
    """설정 로딩 테스트"""
    print("🔧 설정 로딩 테스트...")
    
    # 테스트용 환경 변수 설정
    os.environ["OPENAI_API_KEY"] = "test_key"
    os.environ["S3_BUCKET_NAME"] = "test_bucket"
    
    try:
        # 프로젝트 루트를 Python path에 추가
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config import config
        print(f"  ✅ 환경: {config.app_env}")
        print(f"  ✅ 디버그 모드: {config.debug_mode}")
        print(f"  ✅ S3 버킷: {config.s3_bucket_name}")
        return True
    except Exception as e:
        print(f"  ❌ 설정 로딩 실패: {e}")
        return False

def test_streamlit_import():
    """Streamlit 임포트 테스트"""
    print("\n📱 Streamlit 임포트 테스트...")
    
    try:
        import streamlit as st
        print("  ✅ Streamlit 임포트 성공")
        return True
    except Exception as e:
        print(f"  ❌ Streamlit 임포트 실패: {e}")
        return False

def test_app_syntax():
    """앱 파일 구문 테스트"""
    print("\n🐍 앱 구문 테스트...")
    
    try:
        # Python 구문 검사
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "app.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ app.py 구문 검사 통과")
            return True
        else:
            print(f"  ❌ app.py 구문 오류: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 구문 검사 실패: {e}")
        return False

def test_docker_compose():
    """Docker Compose 설정 테스트"""
    print("\n🐳 Docker Compose 설정 테스트...")
    
    try:
        result = subprocess.run([
            "docker-compose", "config", "--quiet"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ docker-compose.yml 설정 유효")
            return True
        else:
            print(f"  ❌ docker-compose.yml 설정 오류: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Docker Compose 테스트 실패: {e}")
        return False

def test_data_files():
    """데이터 파일 테스트"""
    print("\n📊 데이터 파일 테스트...")
    
    data_files = ["data/business_types.json", "data/regions.json"]
    all_good = True
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  ✅ {file_path} 유효")
            except Exception as e:
                print(f"  ❌ {file_path} JSON 오류: {e}")
                all_good = False
        else:
            print(f"  ❌ {file_path} 파일 없음")
            all_good = False
    
    return all_good

def main():
    """메인 테스트 함수"""
    print("🚀 AI 브랜딩 챗봇 기동 테스트\n")
    
    tests = [
        test_config_loading,
        test_streamlit_import,
        test_app_syntax,
        test_docker_compose,
        test_data_files
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 테스트 결과: {sum(results)}/{len(results)} 통과")
    
    if all(results):
        print("\n🎉 모든 기동 테스트 통과!")
        print("\n다음 단계:")
        print("1. API 키를 .env.local에 설정")
        print("2. streamlit run app.py 로 앱 실행")
        print("3. docker-compose up -d 로 전체 스택 실행")
        return 0
    else:
        print("\n❌ 일부 테스트 실패. 위 오류를 확인하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())