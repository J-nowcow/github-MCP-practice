#!/usr/bin/env python3
"""
PyGithub의 create_file과 update_file 메서드의 반환값을 확인하는 테스트
"""

import os
from dotenv import load_dotenv
from mcp_github.github_client import GitHubClient

# 환경변수 로드
load_dotenv()

def test_pygithub_methods():
    """PyGithub 메서드들의 반환값 확인"""
    
    print("🔍 PyGithub 메서드 반환값 확인")
    print("=" * 40)
    
    try:
        client = GitHubClient()
        repository = client.get_repository("J-nowcow", "github-MCP-practice")
        
        print("✅ 저장소 연결 성공")
        print(f"📁 저장소: {repository.full_name}")
        
        # 간단한 테스트 파일 생성
        test_path = "test_pygithub.txt"
        test_content = "Hello PyGithub Test"
        
        print(f"\n📝 테스트 파일 생성: {test_path}")
        
        # create_file 메서드 호출
        result = repository.create_file(
            path=test_path,
            message="Test PyGithub create_file",
            content=test_content,
            branch="main"
        )
        
        print(f"📊 create_file 반환값 타입: {type(result)}")
        print(f"📊 create_file 반환값: {result}")
        
        if hasattr(result, '__iter__'):
            print(f"📊 반복 가능한 객체: {list(result)}")
            if len(result) >= 2:
                print(f"📊 첫 번째 요소: {result[0]} (타입: {type(result[0])})")
                print(f"📊 두 번째 요소: {result[1]} (타입: {type(result[1])})")
        
        # 파일 삭제 (테스트 후 정리)
        print(f"\n🗑️ 테스트 파일 삭제: {test_path}")
        file_content = repository.get_contents(test_path)
        repository.delete_file(
            path=test_path,
            message="Clean up test file",
            sha=file_content.sha
        )
        print("✅ 테스트 파일 삭제 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # GitHub 토큰 확인
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        exit(1)
    
    test_pygithub_methods()
