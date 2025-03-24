import os

from fastapi import FastAPI, Request, BackgroundTasks

from proxy.api_proxy import APIProxy
from proxy.event_proxy import EventProxy
from environment import ProjectEnvironmentSetup
app = FastAPI(title="Azure Functions Local Proxy")

PROJECT = os.getenv("PROJECT")

@app.api_route("/api/{function}{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_http_function(request: Request, function: str, path: str):
    """Endpoint for HTTP"""
    function_path = f"{PROJECT}.{function}/{path}"
    return await APIProxy(request, function_path).proxy_function()
  
@app.api_route("/event/{function}{path:path}", methods=["POST"])
async def proxy_event_function(request: Request, function_path: str, path: str, background_tasks: BackgroundTasks):
    """Endpoint for EventGridTrigger"""
    function_path = f"{PROJECT}.{function}/{path}"
    return await EventProxy(request, function_path, background_tasks=background_tasks).proxy_function()

@app.on_event("startup")
async def startup_event():
    print(f"Starting in Project Mode with {PROJECT}")
    settuper = ProjectEnvironmentSetup()
    settuper.setup_environment()
    settuper.setup_executor()
    settuper.setup_file_watcher()


    port = int(os.getenv("PORT", 3000))
    print("Azure Functions Local Proxy started")
    print(f"Access your functions in: http://localhost:{port}/api/{{Function}} ou http://localhost:{port}/event/{{Function}}")