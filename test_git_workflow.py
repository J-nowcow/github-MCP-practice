#!/usr/bin/env python3
"""
MCP 클라이언트를 통해 Git 작업을 테스트하는 스크립트
"""

import requests
import json
import time

def test_git_workflow():
    """Git 워크플로우를 테스트합니다."""
    base_url = "http://localhost:8081"
    
    print("🚀 MCP 클라이언트를 통한 Git 워크플로우 테스트 시작")
    
    # 1. 현재 Git 저장소 상태 확인
    print("\n1️⃣ Git 저장소 상태 확인 중...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "query": "Check current Git repository status",
            "thread_id": "git_workflow_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 응답: {result.get('response', '응답 없음')}")
        print(f"📊 상태: {result.get('status', '상태 없음')}")
        print(f"🔧 사용된 도구: {len(result.get('used_tools', []))}개")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")
        return
    
    # 2. 모든 변경사항 스테이징
    print("\n2️⃣ 모든 변경사항 스테이징 중...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "query": "Stage all changes in the Git repository",
            "thread_id": "git_workflow_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 응답: {result.get('response', '응답 없음')}")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")
        return
    
    # 3. 커밋 생성
    print("\n3️⃣ 커밋 생성 중...")
    commit_message = f"Update project files - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    response = requests.post(
        f"{base_url}/chat",
        json={
            "query": f"Create a commit with message: {commit_message}",
            "thread_id": "git_workflow_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 응답: {result.get('response', '응답 없음')}")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")
        return
    
    # 4. 원격 저장소에 푸시
    print("\n4️⃣ 원격 저장소에 푸시 중...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "query": "Push changes to remote repository",
            "thread_id": "git_workflow_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 응답: {result.get('response', '응답 없음')}")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")
        return
    
    print("\n🎉 Git 워크플로우 테스트 완료!")

if __name__ == "__main__":
    test_git_workflow()
