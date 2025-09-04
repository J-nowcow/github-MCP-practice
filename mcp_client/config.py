"""
환경변수 설정 관리
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# .env 파일을 가장 먼저 로드
load_dotenv()


@dataclass
class Config:
    """환경변수 설정 클래스"""
    
    # MCP Server 설정
    MCP_TRANSPORT: str = "streamable_http"  # 고정값
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:3000")
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "3000"))
    MCP_SERVER_PATH: str = os.getenv("MCP_SERVER_PATH", "/mcp")
    
    # Azure OpenAI 설정
    AZURE_OPENAI_ENDPOINT: str = os.getenv(
        "AZURE_OPENAI_ENDPOINT", 
        "https://oai-az01-sbox-poc-145.openai.azure.com/"
    )
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # HTTP 설정
    HTTP_TIMEOUT_SEC: int = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))
    PORT: int = int(os.getenv("PORT", "8081"))
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """MCP 서버 설정을 딕셔너리로 반환 - Streamable HTTP 모드용"""
        # URL 정규화: 끝에 / 강제
        base_url = f"http://{self.MCP_SERVER_HOST}:{self.MCP_SERVER_PORT}{self.MCP_SERVER_PATH}"
        if not base_url.endswith("/"):
            base_url += "/"
            
        return {
            "github": {
                "url": base_url,
                "transport": self.MCP_TRANSPORT,  # "streamable_http" 고정
                "headers": {
                    "Accept": "text/event-stream, application/json",
                    "Content-Type": "application/json",
                    "MCP-Protocol-Version": "2025-03-26"
                },
                "timeout": self.HTTP_TIMEOUT_SEC
            }
        }
    
    def validate(self) -> None:
        """필수 환경변수 검증"""
        if not self.AZURE_OPENAI_API_KEY:
            raise ValueError("AZURE_OPENAI_API_KEY가 설정되지 않았습니다.")
        
        if not self.AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_ENDPOINT가 설정되지 않았습니다.")
        
        # MCP 설정 검증
        mcp_config = self.get_mcp_config()
        if mcp_config["github"]["transport"] != "streamable_http":
            raise ValueError("MCP_TRANSPORT는 'streamable_http'여야 합니다.")


# 전역 설정 인스턴스
config = Config()
