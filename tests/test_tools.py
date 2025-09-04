"""GitHub MCP 도구 테스트 코드."""

import asyncio
import subprocess
import time
from fastmcp import Client


async def test_github_tools():
    """GitHub MCP 도구들을 테스트합니다."""
    print("🧪 GitHub MCP 도구 테스트 시작...")
    
    # 서버를 백그라운드에서 실행
    print("🚀 MCP 서버 시작 중...")
    server_process = subprocess.Popen(
        ["python", "-m", "mcp_github.server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 서버가 시작될 때까지 잠시 대기
    time.sleep(2)
    
    try:
        # FastMCP 클라이언트로 연결
        async with Client("mcp_github/server.py") as client:
            # 1. 도구 목록 확인
            print("\n1️⃣ 도구 목록 확인:")
            tools = await client.list_tools()
            print(f"   📋 등록된 도구 수: {len(tools)}")
            
            tool_names = [tool.name for tool in tools]
            print(f"   🛠️  도구 목록: {tool_names}")
            
            # 2. health 도구 테스트
            print("\n2️⃣ health 도구 테스트:")
            try:
                result = await client.call_tool("health", {})
                print(f"   ✅ health 성공: {result.data}")
            except Exception as e:
                print(f"   ❌ health 실패: {e}")
            
            # 3. getRepo 도구 테스트
            print("\n3️⃣ getRepo 도구 테스트:")
            try:
                result = await client.call_tool("getRepo", {
                    "owner": "J-nowcow",
                    "repo": "github-MCP-practice"
                })
                print(f"   ✅ getRepo 성공")
                if hasattr(result, 'data') and result.data:
                    summary = result.data.get('summary', '')[:100]
                    print(f"   📝 요약: {summary}...")
            except Exception as e:
                print(f"   ❌ getRepo 실패: {e}")
            
            # 4. listPullRequests 도구 테스트
            print("\n4️⃣ listPullRequests 도구 테스트:")
            try:
                result = await client.call_tool("listPullRequests", {
                    "owner": "J-nowcow",
                    "repo": "github-MCP-practice",
                    "state": "open"
                })
                print(f"   ✅ listPullRequests 성공")
                if hasattr(result, 'data') and result.data:
                    count = result.data.get('count', 0)
                    print(f"   📊 PR 개수: {count}개")
            except Exception as e:
                print(f"   ❌ listPullRequests 실패: {e}")
            
            # 5. getPRDiff 도구 테스트 (PR #1이 있다고 가정)
            print("\n5️⃣ getPRDiff 도구 테스트:")
            try:
                result = await client.call_tool("getPRDiff", {
                    "owner": "J-nowcow",
                    "repo": "github-MCP-practice",
                    "number": 1
                })
                print(f"   ✅ getPRDiff 성공")
                if hasattr(result, 'data') and result.data:
                    file_count = result.data.get('file_count', 0)
                    print(f"   📁 변경된 파일: {file_count}개")
            except Exception as e:
                print(f"   ❌ getPRDiff 실패: {e}")
            
            # 6. getFile 도구 테스트
            print("\n6️⃣ getFile 도구 테스트:")
            try:
                result = await client.call_tool("getFile", {
                    "owner": "J-nowcow",
                    "repo": "github-MCP-practice",
                    "path": "README.md",
                    "ref": "HEAD"
                })
                print(f"   ✅ getFile 성공")
                if hasattr(result, 'data') and result.data:
                    file_size = result.data.get('file_size', 0)
                    print(f"   📄 파일 크기: {file_size} bytes")
            except Exception as e:
                print(f"   ❌ getFile 실패: {e}")
    
    finally:
        # 서버 프로세스 종료
        print("\n🛑 MCP 서버 종료 중...")
        server_process.terminate()
        server_process.wait()
    
    print("\n🎯 모든 도구 테스트 완료!")


def test_tools_sync():
    """동기 방식으로 도구 테스트를 실행합니다."""
    asyncio.run(test_github_tools())


if __name__ == "__main__":
    test_tools_sync()
