from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from environment import setup_environment
from proxy.api_proxy import APIProxy
from LocalRunner.proxy.event_proxy import EventProxy

app = FastAPI(title="Azure Functions Local Proxy")

api_proxy = APIProxy()
event_proxy = EventProxy()

@app.api_route("/api/{function_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_http_function(request: Request, function_path: str):
    """Endpoint for HTTP"""
    return await api_proxy.proxy_function(request, function_path)

@app.api_route("/event/{function_path:path}", methods=["POST"])
async def proxy_event_function(request: Request, function_path: str, background_tasks: BackgroundTasks):
    """Endpoint for EventGridTrigger"""
    return await event_proxy.proxy_function(request, function_path, background_tasks=background_tasks)

@app.on_event("startup")
async def startup_event():
    setup_environment()
    print("Azure Functions Local Proxy started")
    print("Access your functions in: http://localhost:3000/api/Project.Function ou http://localhost:3000/event/Project.Function")