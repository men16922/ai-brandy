#!/bin/bash

# AWS 자격증명 설정 스크립트
# 사용법: ./scripts/setup-aws-credentials.sh

set -e

echo "=== AWS 자격증명 설정 ==="
echo ""

# 현재 AWS CLI 설정 확인
echo "현재 AWS CLI 설정:"
aws configure list || echo "AWS CLI가 설정되지 않았습니다."
echo ""

# 자격증명 설정 방법 안내
echo "AWS 자격증명을 설정하는 방법:"
echo ""
echo "1. AWS CLI 프로파일 설정 (권장):"
echo "   aws configure"
echo "   또는"
echo "   aws configure --profile brandy-dev"
echo ""
echo "2. 환경변수로 직접 설정:"
echo "   export AWS_ACCESS_KEY_ID=your_access_key_here"
echo "   export AWS_SECRET_ACCESS_KEY=your_secret_key_here"
echo "   export AWS_DEFAULT_REGION=us-east-1"
echo ""
echo "3. .env.dev 파일에 직접 설정:"
echo "   AWS_ACCESS_KEY_ID=your_access_key_here"
echo "   AWS_SECRET_ACCESS_KEY=your_secret_key_here"
echo ""

# 자격증명 테스트
echo "자격증명 설정 후 테스트:"
echo "  aws sts get-caller-identity"
echo ""

# CloudFormation 스택 상태 확인
echo "CloudFormation 스택 확인:"
echo "  aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --region us-east-1"
echo ""

echo "자격증명 설정이 완료되면 다음 명령어로 애플리케이션을 실행하세요:"
echo "  export \$(cat .env.dev | grep -v '^#' | grep -v '^\$' | xargs)"
echo "  streamlit run app.py"