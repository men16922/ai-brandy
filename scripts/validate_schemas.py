#!/usr/bin/env python3
"""
DynamoDB 테이블 스키마 검증 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.schema_loader import validate_table_schemas


def main():
    """스키마 검증 실행"""
    print("🔍 DynamoDB 테이블 스키마 검증 중...")
    
    errors = validate_table_schemas()
    
    if errors:
        print("❌ 스키마 검증 실패:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ 모든 스키마가 유효합니다!")
        
        # 테이블명 미리보기
        from storage.schema_loader import get_table_names_from_schema
        
        print("\n📋 생성될 테이블 목록:")
        for env in ["local", "dev"]:
            print(f"\n{env.upper()} 환경:")
            table_names = get_table_names_from_schema(env)
            for table_key, table_name in table_names.items():
                print(f"  - {table_key}: {table_name}")


if __name__ == "__main__":
    main()