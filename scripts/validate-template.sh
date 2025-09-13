#!/bin/bash

# CloudFormation 템플릿 검증 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 기본 설정
TEMPLATE_FILE="infrastructure/cloudformation/dynamodb-s3.yaml"
REGION="us-east-1"

print_info "CloudFormation 템플릿 검증 시작"
print_info "템플릿: $TEMPLATE_FILE"

# 템플릿 파일 존재 확인
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    print_error "템플릿 파일을 찾을 수 없습니다: $TEMPLATE_FILE"
    exit 1
fi

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI가 설치되지 않았습니다."
    print_info "설치 가이드: docs/aws-setup.md 참조"
    exit 1
fi

# 자격증명 확인 및 AWS 검증
if aws sts get-caller-identity &> /dev/null; then
    print_success "AWS 자격증명 확인됨"
    
    # AWS 검증
    print_info "AWS CloudFormation으로 템플릿 검증 중..."
    if aws cloudformation validate-template \
        --template-body file://$TEMPLATE_FILE \
        --region $REGION > /dev/null 2>&1; then
        print_success "AWS CloudFormation 검증 통과"
    else
        print_error "AWS CloudFormation 검증 실패"
        aws cloudformation validate-template \
            --template-body file://$TEMPLATE_FILE \
            --region $REGION
        exit 1
    fi
else
    print_warning "AWS 자격증명이 설정되지 않음 (로컬 검증만 수행)"
fi

# 파일 구조 검증
print_info "파일 구조 검증 중..."
if [[ -r "$TEMPLATE_FILE" ]]; then
    FILE_SIZE=$(wc -c < "$TEMPLATE_FILE")
    print_success "  파일 읽기 가능 (크기: ${FILE_SIZE} bytes)"
    
    # 기본 CloudFormation 구조 확인
    if grep -q "AWSTemplateFormatVersion" "$TEMPLATE_FILE"; then
        print_success "  CloudFormation 템플릿 형식 확인됨"
    else
        print_warning "  AWSTemplateFormatVersion이 없습니다"
    fi
    
    if grep -q "Resources:" "$TEMPLATE_FILE"; then
        print_success "  Resources 섹션 확인됨"
    else
        print_error "  Resources 섹션이 없습니다"
        exit 1
    fi
else
    print_error "파일을 읽을 수 없습니다: $TEMPLATE_FILE"
    exit 1
fi

# 템플릿 정보 출력
print_info "템플릿 정보:"
if command -v python3 &> /dev/null; then
    python3 -c "
import re
import sys

try:
    with open('$TEMPLATE_FILE', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 기본 정보 추출 (정규식 사용)
    description = re.search(r'Description:\s*[\"\'](.*?)[\"\']', content)
    if description:
        print(f'  - 설명: {description.group(1)}')
    
    # 섹션별 개수 계산
    parameters = len(re.findall(r'^\s*\w+:\s*$', content, re.MULTILINE))
    resources = len(re.findall(r'^\s*\w+:\s*$', content, re.MULTILINE))
    
    print(f'  - 파일 크기: {len(content)} 문자')
    print(f'  - 라인 수: {len(content.splitlines())}')
    
except Exception as e:
    print(f'  - 정보 추출 실패: {e}')
"
fi

# 모범 사례 체크
print_info "모범 사례 체크:"

# DeletionPolicy 확인
if grep -q "DeletionPolicy.*Retain" "$TEMPLATE_FILE"; then
    print_success "  DeletionPolicy: Retain 설정됨"
else
    print_warning "  DeletionPolicy: Retain이 설정되지 않음"
fi

# 태그 확인
if grep -q "Tags:" "$TEMPLATE_FILE"; then
    print_success "  리소스 태깅 설정됨"
else
    print_warning "  리소스 태깅이 설정되지 않음"
fi

# 암호화 확인
if grep -q "SSESpecification\|BucketEncryption" "$TEMPLATE_FILE"; then
    print_success "  암호화 설정됨"
else
    print_warning "  암호화 설정이 확인되지 않음"
fi

# 조건부 로직 확인
if grep -q "Conditions:" "$TEMPLATE_FILE"; then
    print_success "  조건부 로직 사용됨"
else
    print_warning "  조건부 로직이 사용되지 않음"
fi

# 파라미터 제약 확인
if grep -q "AllowedValues\|AllowedPattern\|MinLength\|MaxLength" "$TEMPLATE_FILE"; then
    print_success "  파라미터 제약 설정됨"
else
    print_warning "  파라미터 제약이 설정되지 않음"
fi

# 메타데이터 확인
if grep -q "Metadata:" "$TEMPLATE_FILE"; then
    print_success "  메타데이터 설정됨"
else
    print_warning "  메타데이터가 설정되지 않음"
fi

print_success "템플릿 검증 완료! 🎉"

# 다음 단계 안내
print_info ""
print_info "다음 단계:"
print_info "1. 배포 테스트: ./scripts/deploy-infrastructure.sh -e dev --dry-run"
print_info "2. 실제 배포: ./scripts/deploy-infrastructure.sh -e dev"
print_info "3. 환경 확인: python3 scripts/check-environment.py -e dev"