#!/usr/bin/env python3
"""
프로젝트 설정 검증 스크립트
"""

import os
import sys

def check_directories():
    """디렉토리 구조 확인"""
    required_dirs = ["config", "core", "adapters", "storage", "utils", "data", "logs", "reports", "docker"]
    
    print("📁 디렉토리 구조 확인:")
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/")
            all_good = False
    
    return all_good

def check_files():
    """필수 파일 확인"""
    required_files = [
        "requirements.txt",
        ".env.local", 
        ".env.dev",
        "docker-compose.yml",
        "Dockerfile",
        "app.py",
        "README.md"
    ]
    
    print("\n📄 필수 파일 확인:")
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            all_good = False
    
    return all_good

def check_config():
    """설정 모듈 확인"""
    print("\n⚙️  설정 모듈 확인:")
    
    config_files = ["config/__init__.py", "config/app_config.py"]
    all_good = True
    
    for file in config_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            all_good = False
    
    # 설정 파일 내용 간단 검증
    if os.path.exists("config/app_config.py"):
        with open("config/app_config.py", "r") as f:
            content = f.read()
            if "class AppConfig" in content and "BaseSettings" in content:
                print("  ✅ AppConfig 클래스 정의됨")
            else:
                print("  ❌ AppConfig 클래스 누락")
                all_good = False
    
    return all_good

def main():
    """메인 검증 함수"""
    print("🚀 AI 브랜딩 챗봇 프로젝트 설정 검증\n")
    
    checks = [
        check_directories(),
        check_files(),
        check_config()
    ]
    
    if all(checks):
        print("\n🎉 모든 설정이 완료되었습니다!")
        print("\n다음 단계:")
        print("1. API 키를 .env.local 파일에 설정")
        print("2. docker-compose up -d 로 서비스 시작")
        print("3. http://localhost:8501 에서 애플리케이션 확인")
        return 0
    else:
        print("\n❌ 일부 설정에 문제가 있습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main())