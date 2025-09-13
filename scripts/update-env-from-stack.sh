#!/bin/bash

# CloudFormation 스택 출력을 기반으로 .env.dev 파일 업데이트

set -e

STACK_NAME="brandy-infrastructure-dev"
ENV_FILE=".env.dev"

echo "🔄 CloudFormation 스택에서 리소스 정보 가져오는 중..."

# 스택 출력 가져오기
OUTPUTS=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs' \
  --output json)

if [ $? -ne 0 ]; then
    echo "❌ 스택 정보를 가져올 수 없습니다. 스택이 배포되었는지 확인하세요."
    exit 1
fi

# 출력에서 값 추출
S3_BUCKET=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="DemoS3BucketName") | .OutputValue')
REGIONS_TABLE=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="DemoRegionsTableName") | .OutputValue')
BUSINESS_TYPES_TABLE=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="DemoBusinessTypesTableName") | .OutputValue')
WORKFLOW_TABLE=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="DemoWorkflowTableName") | .OutputValue')
APP_ROLE_ARN=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="DemoApplicationRoleArn") | .OutputValue')

echo "✅ 리소스 정보 수집 완료:"
echo "  - S3 버킷: $S3_BUCKET"
echo "  - 지역 테이블: $REGIONS_TABLE"
echo "  - 업종 테이블: $BUSINESS_TYPES_TABLE"
echo "  - 워크플로 테이블: $WORKFLOW_TABLE"

# .env.dev 파일 생성/업데이트
cat > $ENV_FILE << EOF
# AI 브랜딩 챗봇 - Dev 환경 설정 (CloudFormation 자동 생성)
APP_ENV=dev
LOG_LEVEL=INFO

# AWS 설정
AWS_DEFAULT_REGION=us-east-1

# CloudFormation에서 생성된 리소스들
S3_BUCKET_NAME=$S3_BUCKET
DYNAMODB_TABLE_REGIONS=$REGIONS_TABLE
DYNAMODB_TABLE_BUSINESS_TYPES=$BUSINESS_TYPES_TABLE
DYNAMODB_TABLE_WORKFLOW=$WORKFLOW_TABLE
APPLICATION_ROLE_ARN=$APP_ROLE_ARN

# API 키들 (수동 설정 필요)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangChain 설정 (선택사항)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ai-branding-chatbot-dev

# 벡터 데이터베이스 설정 (Dev 환경에서는 Bedrock Knowledge Base 사용)
# BEDROCK_KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
# BEDROCK_REGION=us-east-1

# 성능 설정
MAX_CONCURRENT_CHAINS=3
CHAIN_TIMEOUT_SECONDS=30
ENABLE_CHAIN_CACHING=true

# 디버그 설정
DEBUG_MODE=false
VERBOSE_LOGGING=false
EOF

echo "✅ $ENV_FILE 파일이 업데이트되었습니다!"
echo ""
echo "⚠️  다음 단계:"
echo "1. $ENV_FILE 파일에서 API 키들을 실제 값으로 수정하세요"
echo "2. 애플리케이션 실행: export \$(cat $ENV_FILE | xargs) && streamlit run app.py"
echo ""
echo "📋 현재 설정된 리소스들:"
cat $ENV_FILE | grep -E "^(S3_BUCKET_NAME|DYNAMODB_TABLE_|APPLICATION_ROLE_ARN)="