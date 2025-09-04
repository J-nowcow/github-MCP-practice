#!/usr/bin/env python3
"""
간단한 Git 상태 확인 테스트
"""

import requests
import json

def test_simple_git():
    """간단한 Git 테스트를 수행합니다."""
    base_url = "http://localhost:8081"
    
    print("🔍 간단한 Git 상태 확인 테스트")
    
    # Git 저장소 상태 확인
    print("\n1️⃣ Git 저장소 상태 확인...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "query": "What is the current Git status?",
            "thread_id": "simple_test_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 응답: {result.get('response', '응답 없음')[:200]}...")
        print(f"📊 상태: {result.get('status', '상태 없음')}")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_simple_git()
