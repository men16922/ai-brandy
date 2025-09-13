# 🚀 빠른 명령어 모음

## 환경변수 설정 (원라이너)

```bash
# 모든 환경변수를 한 번에 설정
eval $(aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output text | awk '{print "export " $1 "=" $2}' | sed 's/DemoS3BucketName/S3_BUCKET_NAME/; s/DemoRegionsTableName/DYNAMODB_TABLE_REGIONS/; s/DemoBusinessTypesTableName/DYNAMODB_TABLE_BUSINESS_TYPES/; s/DemoWorkflowTableName/DYNAMODB_TABLE_WORKFLOW/') && export APP_ENV=dev AWS_DEFAULT_REGION=us-east-1
```

## 개별 리소스 확인

```bash
# S3 버킷 이름
aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --query "Stacks[0].Outputs[?OutputKey=='DemoS3BucketName'].OutputValue" --output text

# DynamoDB 테이블들
aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --query "Stacks[0].Outputs[?contains(OutputKey, 'Table')].{Name:OutputKey,Value:OutputValue}" --output table
```

## 상태 확인

```bash
# CloudFormation 스택 상태
aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --query "Stacks[0].StackStatus" --output text

# 모든 출력 보기
aws cloudformation describe-stacks --stack-name brandy-infrastructure-dev --query "Stacks[0].Outputs" --output table
```

## 애플리케이션 실행

```bash
# 1. 환경변수 설정
source scripts/set-env.sh

# 2. API 키 설정 (실제 키로 교체)
export OPENAI_API_KEY=your_actual_openai_key
export GOOGLE_API_KEY=your_actual_google_key

# 3. 애플리케이션 실행
streamlit run app.py
```

## 정리

```bash
# 스택 삭제
./scripts/deploy-infrastructure.sh -e dev --delete
```