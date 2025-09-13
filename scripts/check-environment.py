#!/usr/bin/env python3
"""
환경별 리소스 상태 확인 스크립트
"""

import sys
import os
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.unified_storage import UnifiedStorage
from utils.logger import get_logger


def check_local_environment():
    """Local 환경 상태 확인"""
    print("🔍 Local 환경 확인 중...")
    
    # Docker 서비스 확인
    docker_services = [
        ("DynamoDB Local", "http://localhost:8000"),
        ("MinIO", "http://localhost:9000"),
        ("Chroma DB", "http://localhost:8003")
    ]
    
    import requests
    
    for service_name, url in docker_services:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {service_name}: 정상 ({url})")
        except Exception as e:
            print(f"❌ {service_name}: 연결 실패 ({url}) - {str(e)}")
    
    # 저장소 초기화 테스트
    try:
        storage = UnifiedStorage("local")
        health_results = storage.health_check()
        
        print("\n📊 저장소 헬스체크:")
        for result in health_results:
            status_icon = "✅" if result.status == "healthy" else "❌"
            print(f"{status_icon} {result.service_name}: {result.message}")
            if result.response_time_ms:
                print(f"   응답시간: {result.response_time_ms:.1f}ms")
        
    except Exception as e:
        print(f"❌ 저장소 초기화 실패: {str(e)}")


def check_aws_environment(environment="dev"):
    """AWS 환경 상태 확인"""
    print(f"🔍 AWS {environment.upper()} 환경 확인 중...")
    
    try:
        # AWS 자격증명 확인
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS 자격증명: {identity.get('Arn', 'Unknown')}")
        
        # CloudFormation 스택 확인
        cf = boto3.client('cloudformation')
        stack_name = f"brandy-infrastructure-{environment}"
        
        try:
            response = cf.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            stack_status = stack['StackStatus']
            
            if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                print(f"✅ CloudFormation 스택: {stack_name} ({stack_status})")
                
                # 스택 출력 정보 표시
                outputs = stack.get('Outputs', [])
                if outputs:
                    print("\n📋 스택 출력:")
                    for output in outputs:
                        print(f"  - {output['OutputKey']}: {output['OutputValue']}")
                
            else:
                print(f"⚠️  CloudFormation 스택: {stack_name} ({stack_status})")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                print(f"❌ CloudFormation 스택을 찾을 수 없습니다: {stack_name}")
                print(f"   배포 명령어: ./scripts/deploy-infrastructure.sh -e {environment}")
            else:
                raise
        
        # 저장소 리소스 확인
        try:
            storage = UnifiedStorage(environment)
            health_results = storage.health_check()
            
            print(f"\n📊 AWS 리소스 헬스체크:")
            for result in health_results:
                status_icon = "✅" if result.status == "healthy" else "❌"
                print(f"{status_icon} {result.service_name}: {result.message}")
                if result.response_time_ms:
                    print(f"   응답시간: {result.response_time_ms:.1f}ms")
            
        except Exception as e:
            print(f"❌ AWS 리소스 확인 실패: {str(e)}")
            
    except Exception as e:
        if "credentials" in str(e).lower() or "unable to locate credentials" in str(e).lower():
            print("❌ AWS 자격증명이 설정되지 않았습니다.")
            print("   설정 방법:")
            print("   1. AWS Configure: aws configure")
            print("   2. 환경변수: export AWS_ACCESS_KEY_ID=... && export AWS_SECRET_ACCESS_KEY=...")
            print("   3. 자세한 가이드: docs/aws-setup.md")
        else:
            print(f"❌ AWS 환경 확인 실패: {str(e)}")
    except Exception as e:
        print(f"❌ AWS 환경 확인 실패: {str(e)}")


def check_configuration_files():
    """설정 파일 확인"""
    print("🔍 설정 파일 확인 중...")
    
    config_files = [
        (".env.local", "Local 환경 변수"),
        (".env.dev", "Dev 환경 변수"),
        ("docker-compose.yml", "Local Docker 설정"),
        ("infrastructure/config/aws-dev.json", "AWS Dev 설정"),
        ("storage/schemas/dynamodb_tables.json", "DynamoDB 스키마"),
        ("infrastructure/cloudformation/dynamodb-tables.yaml", "CloudFormation 템플릿")
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} (파일 없음)")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="환경별 리소스 상태 확인")
    parser.add_argument("-e", "--environment", 
                       choices=["local", "dev", "all"], 
                       default="all",
                       help="확인할 환경 (기본값: all)")
    
    args = parser.parse_args()
    
    print("🚀 AI 브랜딩 챗봇 환경 상태 확인")
    print("=" * 50)
    
    # 설정 파일 확인
    check_configuration_files()
    print()
    
    if args.environment in ["local", "all"]:
        check_local_environment()
        print()
    
    if args.environment in ["dev", "all"]:
        check_aws_environment("dev")
        print()
    
    print("🎉 환경 상태 확인 완료!")


if __name__ == "__main__":
    main()