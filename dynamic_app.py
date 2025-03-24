import os

from fastapi import FastAPI, Request, BackgroundTasks

from environment import DynamicEnvironmentSetup
from proxy.api_proxy import APIProxy
from proxy.event_proxy import EventProxy

app = FastAPI(title="Azure Functions Local Proxy")

@app.api_route("/api/{function_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_http_function(request: Request, function_path: str):
    """Endpoint for HTTP"""
    return await APIProxy(request, function_path).proxy_function()
  
@app.api_route("/event/{function_path:path}", methods=["POST"])
async def proxy_event_function(request: Request, function_path: str, background_tasks: BackgroundTasks):
    """Endpoint for EventGridTrigger"""
    return await EventProxy(request, function_path, background_tasks=background_tasks).proxy_function()

@app.on_event("startup")
async def startup_event():
    print("Starting in Dynamic Mode")
    settuper = DynamicEnvironmentSetup()
    settuper.setup_environment()
    settuper.setup_executor()
    settuper.setup_file_watcher()

    port = int(os.getenv("PORT", 3000))
    print("Azure Functions Local Proxy started")
    print(f"Access your functions in: http://localhost:{port}/api/Project.Function ou http://localhost:{port}/event/Project.Function")