#!/usr/bin/env python3
"""
Dev 환경 DynamoDB 테이블에 초기 데이터 로드
"""

import sys
import os
import json
import boto3
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.data_models import RegionData, BusinessTypeData


def load_json_data(file_path: str):
    """JSON 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {file_path} - {str(e)}")
        return None


def convert_regions_to_dynamodb_items(regions_data):
    """지역 데이터를 DynamoDB 아이템으로 변환"""
    items = []
    
    for region, districts in regions_data.items():
        for district, info in districts.items():
            region_data = RegionData(
                region=region,
                district=district,
                characteristics=info.get("characteristics", []),
                foot_traffic=info.get("foot_traffic", ""),
                rent_level=info.get("rent_level", "")
            )
            items.append(region_data.to_dynamodb_item("demo"))
    
    return items


def convert_business_types_to_dynamodb_items(business_types_data):
    """업종 데이터를 DynamoDB 아이템으로 변환"""
    items = []
    
    for business_type, info in business_types_data.items():
        business_data = BusinessTypeData(
            business_type=business_type,
            keywords=info.get("keywords", []),
            typical_size=info.get("typical_size", [0, 0]),
            style_suggestions=info.get("style_suggestions", [])
        )
        items.append(business_data.to_dynamodb_item("demo"))
    
    return items


def batch_write_items(dynamodb, table_name, items):
    """배치로 DynamoDB에 아이템 삽입"""
    try:
        table = dynamodb.Table(table_name)
        success_count = 0
        
        # DynamoDB 배치 쓰기는 최대 25개씩 처리
        batch_size = 25
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            with table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.put_item(Item=item)
                    success_count += 1
        
        return success_count
        
    except Exception as e:
        print(f"❌ 배치 쓰기 실패: {str(e)}")
        return 0


def check_table_has_data(dynamodb, table_name):
    """테이블에 데이터가 있는지 확인"""
    try:
        table = dynamodb.Table(table_name)
        response = table.scan(Limit=1)
        return len(response.get('Items', [])) > 0
    except Exception as e:
        print(f"⚠️  테이블 확인 실패: {table_name} - {str(e)}")
        return False


def main():
    """메인 함수"""
    print("🚀 Dev 환경 DynamoDB 초기 데이터 로드 시작")
    
    # DynamoDB 클라이언트 초기화
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        print("✅ DynamoDB 연결 성공")
    except Exception as e:
        print(f"❌ DynamoDB 연결 실패: {str(e)}")
        return False
    
    # 테이블 이름들
    tables = {
        "regions": "brandy-regions-demo",
        "business_types": "brandy-business-types-demo"
    }
    
    # 지역 데이터 로드
    print("\n📍 지역 데이터 로드 중...")
    regions_table = tables["regions"]
    
    if check_table_has_data(dynamodb, regions_table):
        print(f"ℹ️  {regions_table}에 이미 데이터가 있습니다.")
    else:
        regions_data = load_json_data("data/regions.json")
        if regions_data:
            regions_items = convert_regions_to_dynamodb_items(regions_data)
            success_count = batch_write_items(dynamodb, regions_table, regions_items)
            print(f"✅ 지역 데이터 로드 완료: {success_count}/{len(regions_items)} 아이템")
        else:
            print("❌ 지역 데이터 로드 실패")
    
    # 업종 데이터 로드
    print("\n🏢 업종 데이터 로드 중...")
    business_types_table = tables["business_types"]
    
    if check_table_has_data(dynamodb, business_types_table):
        print(f"ℹ️  {business_types_table}에 이미 데이터가 있습니다.")
    else:
        business_types_data = load_json_data("data/business_types.json")
        if business_types_data:
            business_items = convert_business_types_to_dynamodb_items(business_types_data)
            success_count = batch_write_items(dynamodb, business_types_table, business_items)
            print(f"✅ 업종 데이터 로드 완료: {success_count}/{len(business_items)} 아이템")
        else:
            print("❌ 업종 데이터 로드 실패")
    
    # 결과 확인
    print("\n📊 데이터 로드 결과 확인:")
    for table_key, table_name in tables.items():
        try:
            table = dynamodb.Table(table_name)
            response = table.scan(Select='COUNT')
            item_count = response.get('Count', 0)
            print(f"  - {table_name}: {item_count} 아이템")
        except Exception as e:
            print(f"  - {table_name}: 확인 실패 - {str(e)}")
    
    print("\n🎉 초기 데이터 로드 완료!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)