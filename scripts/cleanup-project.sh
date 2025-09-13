#!/bin/bash

# 프로젝트 정리 스크립트
# 불필요한 파일들과 캐시를 정리합니다

set -e

echo "=== AI 브랜딩 챗봇 프로젝트 정리 ==="
echo ""

# Python 캐시 정리
echo "🧹 Python 캐시 정리..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
find . -name ".Python" -delete 2>/dev/null || true
find . -name "pip-log.txt" -delete 2>/dev/null || true
find . -name "pip-delete-this-directory.txt" -delete 2>/dev/null || true

# 로그 파일 정리
echo "📝 로그 파일 정리..."
rm -f logs/*.log 2>/dev/null || true

# Docker 정리 (선택사항)
read -p "Docker 볼륨과 이미지를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐳 Docker 정리..."
    docker-compose down -v 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
fi

# 임시 파일 정리
echo "🗑️  임시 파일 정리..."
rm -f .DS_Store 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -f *.temp 2>/dev/null || true

echo ""
echo "✅ 프로젝트 정리 완료!"
echo ""
echo "다음 명령어로 애플리케이션을 실행할 수 있습니다:"
echo "  source venv/bin/activate"
echo "  source .env.local  # 또는 .env.dev"
echo "  streamlit run app.py"