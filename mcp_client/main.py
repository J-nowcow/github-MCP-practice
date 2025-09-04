"""
FastAPI 엔트리포인트 - LangGraph 에이전트 통합
"""
import asyncio
import logging
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from mcp_client.config import config
from mcp_client.agent.workflow import MCPAgentWorkflow
from mcp_client.schemas import ChatRequest, ChatResponse, HealthResponse

# 로깅 설정
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 앱 수명주기 관리"""
    # 앱 시작 시 초기화
    cfg = config
    app.state.cfg = cfg
    
    # MultiServerMCPClient 직접 생성 (컨텍스트 매니저 불필요)
    from langchain_mcp_adapters.client import MultiServerMCPClient
    app.state.mcp_client = MultiServerMCPClient(cfg.get_mcp_config())
    app.state.workflow = None
    app.state.tools_cache = None
    app.state.status = "starting"
    
    logger.info("MCP Client 앱 시작 중...")
    
    # "준비 시도"는 비차단 태스크로 (서버가 늦게 떠도 앱은 기동)
    async def warmup():
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"MCP 서버 연결 시도 {retry_count + 1}/{max_retries}")
                
                # 공식 문서에 따라 직접 도구 로딩 (컨텍스트 매니저 불필요)
                tools = await app.state.mcp_client.get_tools()
                app.state.tools_cache = tools
                
                # 워크플로우 초기화
                app.state.workflow = MCPAgentWorkflow(app.state.mcp_client)
                
                app.state.status = "ready"
                
                # 상태 확인
                health_status = await app.state.workflow.health_check()
                logger.info("워크플로우 상태", extra={"status": health_status})
                
                logger.info("MCP 서버 연결 성공!")
                break
                    
            except Exception as e:
                retry_count += 1
                logger.warning(f"MCP 서버 연결 실패 (시도 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    # 2초 대기 후 재시도
                    await asyncio.sleep(2)
                else:
                    app.state.status = f"connecting_failed: {type(e).__name__}"
                    logger.error("최대 재시도 횟수 초과, MCP 연결 실패")
                    # MCP 서버가 없어도 기본 워크플로우는 생성
                    app.state.workflow = None
    
    # 비차단으로 warmup 실행
    asyncio.create_task(warmup())
    
    logger.info("MCP Client 앱 시작 완료")
    
    yield
    
    # 앱 종료 시 정리
    logger.info("MCP Client 앱 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title="MCP Client",
    description="LangGraph 기반 MCP Server 연동 클라이언트",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        status = app.state.status
        mcp_client = app.state.mcp_client
        workflow = app.state.workflow
        tools_cache = app.state.tools_cache
        
        if status == "ready" and workflow and tools_cache:
            # 워크플로우 상태 확인
            try:
                workflow_status = await workflow.health_check()
                return HealthResponse(
                    status="ok",
                    details={
                        "mcp_client": workflow_status.get("mcp_client", {}),
                        "workflow": workflow_status.get("workflow", "ready"),
                        "tools_available": len(tools_cache)
                    }
                )
            except Exception as e:
                logger.error(f"워크플로우 상태 확인 실패: {e}")
                return HealthResponse(
                    status="degraded",
                    details={
                        "mcp_client": "workflow_error",
                        "workflow": "error",
                        "tools_available": len(tools_cache) if tools_cache else 0,
                        "error": str(e)
                    }
                )
        elif status == "starting":
            return HealthResponse(
                status="starting",
                details={
                    "mcp_client": "initializing",
                    "workflow": "initializing",
                    "tools_available": 0,
                    "note": "앱 시작 중..."
                }
            )
        elif "connecting_failed" in status:
            return HealthResponse(
                status="degraded",
                details={
                    "mcp_client": "connection_failed",
                    "workflow": "not_available",
                    "tools_available": 0,
                    "note": f"MCP 서버 연결 실패: {status}"
                }
            )
        else:
            return HealthResponse(
                status="degraded",
                details={
                    "mcp_client": "unknown",
                    "workflow": "unknown",
                    "tools_available": 0,
                    "note": f"알 수 없는 상태: {status}"
                }
            )
        
    except Exception as e:
        logger.error(f"헬스체크 실패: {e}")
        return HealthResponse(status="error", details={"error": str(e)})


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 엔드포인트"""
    mcp_client = app.state.mcp_client
    workflow = app.state.workflow
    tools_cache = app.state.tools_cache
    
    if not mcp_client:
        raise HTTPException(status_code=503, detail="MCP 클라이언트가 초기화되지 않았습니다")
    
    # 필요 시점에 도구 로딩(재시도 포함)
    if tools_cache is None:
        try:
            # 공식 문서에 따라 직접 도구 로딩 (컨텍스트 매니저 불필요)
            tools = await mcp_client.get_tools()
            app.state.tools_cache = tools
            app.state.status = "ready"
            tools_cache = tools
        except Exception as e:
            app.state.status = f"connect_error: {type(e).__name__}"
            logger.error(f"도구 로딩 실패: {e}")
            raise HTTPException(503, f"MCP connect/load failed: {e}")
    
    if not workflow:
        try:
            workflow = MCPAgentWorkflow(mcp_client)
            app.state.workflow = workflow
        except Exception as e:
            logger.error(f"워크플로우 생성 실패: {e}")
            raise HTTPException(503, f"워크플로우 생성 실패: {e}")
    
    try:
        logger.info(f"채팅 요청: {request.query[:100]}...")
        
        # 워크플로우 실행 (컨텍스트 매니저 불필요)
        result = await workflow.invoke(
            query=request.query,
            thread_id=request.thread_id
        )
        
        # 추적 정보 생성
        trace = {
            "tool_names": [tool.get("name", "unknown") for tool in result.get("used_tools", [])],
            "model_rounds": len(result.get("messages", [])),
            "thread_id": request.thread_id
        }
        
        logger.info(f"채팅 완료: {len(result.get('used_tools', []))}개 툴 사용")
        
        return ChatResponse(
            response=result.get("response", "응답을 생성할 수 없습니다"),
            used_tools=result.get("used_tools", []),
            status=result.get("status", "error"),
            trace=trace
        )
        
    except Exception as e:
        logger.error(f"채팅 실패: {e}")
        return ChatResponse(
            response=f"에러가 발생했습니다: {str(e)}",
            used_tools=[],
            status="error",
            trace={"error": str(e)}
        )


@app.get("/workflow/info")
async def get_workflow_info():
    """워크플로우 정보 조회"""
    workflow = app.state.workflow
    
    if not workflow:
        raise HTTPException(status_code=503, detail="워크플로우가 초기화되지 않았습니다")
    
    try:
        info = workflow.get_workflow_info()
        return {
            "status": "success",
            "workflow_info": info
        }
    except Exception as e:
        logger.error(f"워크플로우 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"워크플로우 정보 조회 실패: {str(e)}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MCP Client API",
        "version": "0.1.0",
        "status": app.state.status,
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "workflow_info": "/workflow/info"
        }
    }
