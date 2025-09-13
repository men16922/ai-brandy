#!/bin/bash

# AI 브랜딩 챗봇 인프라 배포 스크립트

set -e

# 기본 설정
PROJECT_NAME="brandy"
STACK_NAME="${PROJECT_NAME}-infrastructure"
TEMPLATE_FILE="infrastructure/cloudformation/dynamodb-s3.yaml"
CONFIG_FILE="infrastructure/config/aws-${ENVIRONMENT}.json"
REGION="us-east-1"

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

# 도움말 출력
show_help() {
    echo "사용법: $0 [OPTIONS]"
    echo ""
    echo "옵션:"
    echo "  -e, --environment ENV    배포 환경 (dev, prod) [기본값: dev]"
    echo "  -r, --region REGION      AWS 리전 [기본값: us-east-1]"
    echo "  -p, --project PROJECT    프로젝트 이름 [기본값: brandy]"
    echo "  --delete                 스택 삭제"
    echo "  --validate               템플릿 검증만 수행"
    echo "  --dry-run               변경사항 미리보기"
    echo "  -h, --help              도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0 -e dev                    # dev 환경에 배포"
    echo "  $0 -e prod -r ap-northeast-2 # prod 환경을 서울 리전에 배포"
    echo "  $0 --validate                # 템플릿 검증"
    echo "  $0 --delete -e dev           # dev 환경 스택 삭제"
}

# 파라미터 파싱
ENVIRONMENT="dev"
DELETE_STACK=false
VALIDATE_ONLY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --delete)
            DELETE_STACK=true
            shift
            ;;
        --validate)
            VALIDATE_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    print_error "지원하지 않는 환경: $ENVIRONMENT (dev, prod만 지원)"
    exit 1
fi

# 스택 이름 업데이트
STACK_NAME="${PROJECT_NAME}-infrastructure-${ENVIRONMENT}"

print_info "배포 설정:"
echo "  - 프로젝트: $PROJECT_NAME"
echo "  - 환경: $ENVIRONMENT"
echo "  - 리전: $REGION"
echo "  - 스택명: $STACK_NAME"
echo ""

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI가 설치되지 않았습니다."
    print_info "설치 가이드: docs/aws-setup.md 참조"
    exit 1
fi

# AWS 자격증명 확인
print_info "AWS 자격증명 확인 중..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS 자격증명이 설정되지 않았습니다."
    print_info ""
    print_info "자격증명 설정 방법:"
    print_info "1. AWS Configure: aws configure"
    print_info "2. 환경변수: export AWS_ACCESS_KEY_ID=... && export AWS_SECRET_ACCESS_KEY=..."
    print_info "3. IAM Role (EC2/Lambda에서 실행시)"
    print_info ""
    print_info "자세한 설정 가이드: docs/aws-setup.md"
    exit 1
fi

# 자격증명 정보 출력
CALLER_IDENTITY=$(aws sts get-caller-identity)
if command -v jq &> /dev/null; then
    USER_ARN=$(echo $CALLER_IDENTITY | jq -r '.Arn // "N/A"')
    ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account // "N/A"')
    print_success "AWS 자격증명 확인 완료"
    print_info "  사용자: $USER_ARN"
    print_info "  계정: $ACCOUNT_ID"
else
    print_success "AWS 자격증명 확인 완료"
    print_info "  자격증명 정보:"
    echo "$CALLER_IDENTITY"
fi

# 템플릿 파일 존재 확인
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    print_error "템플릿 파일을 찾을 수 없습니다: $TEMPLATE_FILE"
    exit 1
fi

# 템플릿 검증
print_info "CloudFormation 템플릿 검증 중..."
if aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION > /dev/null; then
    print_success "템플릿 검증 완료"
else
    print_error "템플릿 검증 실패"
    exit 1
fi

# 검증만 수행하는 경우
if [[ "$VALIDATE_ONLY" == true ]]; then
    print_success "템플릿 검증이 완료되었습니다."
    exit 0
fi

# 스택 삭제
if [[ "$DELETE_STACK" == true ]]; then
    print_warning "스택 삭제를 시작합니다: $STACK_NAME"
    read -p "정말로 삭제하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "스택 삭제 중..."
        aws cloudformation delete-stack \
            --stack-name $STACK_NAME \
            --region $REGION
        
        print_info "스택 삭제 완료 대기 중..."
        aws cloudformation wait stack-delete-complete \
            --stack-name $STACK_NAME \
            --region $REGION
        
        print_success "스택이 성공적으로 삭제되었습니다."
    else
        print_info "스택 삭제가 취소되었습니다."
    fi
    exit 0
fi

# 스택 존재 여부 확인
STACK_EXISTS=false
if aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION &> /dev/null; then
    STACK_EXISTS=true
fi

# 파라미터 설정
PARAMETERS="ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
PARAMETERS="$PARAMETERS ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME"

# Dry run (변경사항 미리보기)
if [[ "$DRY_RUN" == true ]]; then
    print_info "변경사항 미리보기 생성 중..."
    
    if [[ "$STACK_EXISTS" == true ]]; then
        # 변경 세트 생성
        CHANGESET_NAME="preview-$(date +%Y%m%d-%H%M%S)"
        aws cloudformation create-change-set \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters $PARAMETERS \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
        
        # 변경 세트 대기
        aws cloudformation wait change-set-create-complete \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --region $REGION
        
        # 변경사항 출력
        aws cloudformation describe-change-set \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --region $REGION \
            --query 'Changes[*].[Action,ResourceChange.LogicalResourceId,ResourceChange.ResourceType]' \
            --output table
        
        # 변경 세트 삭제
        aws cloudformation delete-change-set \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --region $REGION
    else
        print_info "새로운 스택이 생성됩니다."
        aws cloudformation estimate-template-cost \
            --template-body file://$TEMPLATE_FILE \
            --parameters $PARAMETERS \
            --region $REGION \
            --query 'Url' \
            --output text
    fi
    exit 0
fi

# 스택 배포
if [[ "$STACK_EXISTS" == true ]]; then
    print_info "기존 스택 업데이트 중: $STACK_NAME"
    
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters $PARAMETERS \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    print_info "스택 업데이트 완료 대기 중..."
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    print_success "스택이 성공적으로 업데이트되었습니다."
else
    print_info "새로운 스택 생성 중: $STACK_NAME"
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters $PARAMETERS \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --enable-termination-protection
    
    print_info "스택 생성 완료 대기 중..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    print_success "스택이 성공적으로 생성되었습니다."
fi

# 스택 출력 정보 표시
print_info "스택 출력 정보:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue,Description]' \
    --output table

print_success "인프라 배포가 완료되었습니다! 🎉"