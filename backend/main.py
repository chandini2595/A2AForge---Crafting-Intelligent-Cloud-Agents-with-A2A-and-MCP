from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.append('..')
from agents.coordinator import CoordinatorAgent

app = FastAPI(title="AWS Multi-Agent System")

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including file:// protocol
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

coordinator = CoordinatorAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: dict
    success: bool

@app.get("/")
async def root():
    return {"message": "AWS Multi-Agent System API", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message and return agent response"""
    try:
        response = coordinator.process_request(request.message)
        return ChatResponse(
            response=response,
            success="error" not in response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instances")
async def list_instances():
    """List all EC2 instances"""
    return coordinator.ec2_agent.list_instances()

@app.get("/buckets")
async def list_buckets():
    """List all S3 buckets"""
    return coordinator.s3_agent.list_buckets()

@app.get("/status")
async def get_status():
    """Get system status with A2A communication demo"""
    # Use A2A to gather info from all agents
    ec2_info = coordinator.query_agent("EC2Agent", "How many running instances?")
    s3_info = coordinator.query_agent("S3Agent", "How many buckets?")
    
    # Check LLM client type
    llm_client_type = type(coordinator.perplexity).__name__
    cache_size = len(coordinator.perplexity.cache) if hasattr(coordinator.perplexity, 'cache') else 0
    
    return {
        "status": "running",
        "a2a_enabled": True,
        "llm_client": llm_client_type,
        "cache_size": cache_size,
        "agents": {
            "coordinator": coordinator.name,
            "ec2": coordinator.ec2_agent.name,
            "s3": coordinator.s3_agent.name
        },
        "resources": {
            "ec2": ec2_info,
            "s3": s3_info
        },
        "conversation_history": coordinator.get_conversation_history()[-5:]  # Last 5 messages
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
