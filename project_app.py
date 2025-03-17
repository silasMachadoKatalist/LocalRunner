from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import json

from environment import setup_environment
from proxy.api_proxy import APIProxy
from LocalRunner.proxy.event_proxy import EventProxy
from function_info import find_function_info
from utils import parse_path_to_function_name

app = FastAPI(title="Azure Functions Local Proxy (Project Mode)")

api_proxy = APIProxy()
event_proxy = EventProxy()

# Global variable to store loaded function info
loaded_function_info = None

@app.on_event("startup")
async def startup_event():
    global loaded_function_info
    setup_environment()
    
    project_function = os.getenv("PROJECT")
    if not project_function:
        raise RuntimeError("PROJECT environment variable is not set.")
    
    print(f"Starting Azure Function: {project_function}")
    project, function_name, _ = parse_path_to_function_name(project_function)
    func_info = find_function_info(project, function_name)
    
    if not func_info:
        raise RuntimeError(f"Function '{project_function}' not found.")
    
    if not func_info.module:
        from function_info import load_function_module
        if not load_function_module(func_info):
            raise RuntimeError(f"Could not load function module for '{project_function}'")
    
    loaded_function_info = func_info
    print(f"Function '{project_function}' loaded successfully.")
    
    # Load the function.json file to determine bindings
    function_json_path = os.path.join(func_info.function_dir, "function.json")
    if not os.path.exists(function_json_path):
        raise RuntimeError(f"function.json not found for '{project_function}'")
    
    with open(function_json_path, "r") as f:
        function_config = json.load(f)
    
    # Determine the binding type and configure the route
    for binding in function_config.get("bindings", []):
        binding_type = binding.get("type")
        if binding_type == "httpTrigger":
            methods = binding.get("methods", ["get"])  # Default to GET if not specified
            route = binding.get("route", "/")  # Use the route defined in function.json or default to "/"
            # Ensure the route starts with "/"
            if not route.startswith("/"):
                route = f"/{route}"
        
            app.add_api_route(
                route,
                direct_http_function,
                methods=[method.upper() for method in methods]
            )
            print(f"Registered HTTP trigger route at '{route}' with methods {methods}")
        elif binding_type == "eventGridTrigger":
            app.add_api_route(
                "/", 
                direct_event_function, 
                methods=["POST"]
            )
            print("Registered EventGrid trigger route at '/'")
        else:
            print(f"Unsupported binding type: {binding_type}")
            
    for route in app.routes:
        print(f"Route: {route.path}, Methods: {route.methods}")

async def direct_http_function(request: Request):
    """Direct HTTP function execution when PROJECT is set"""
    print("direct_http_function called")
    if loaded_function_info:
        # Use project and function_name to construct the full name
        function_full_name = f"{loaded_function_info.project}.{loaded_function_info.function_name}"
        print(f"Processing request for function: {function_full_name}")
        
        # Pass the PROJECT environment variable directly
        response = await api_proxy.proxy_function(request, os.getenv("PROJECT"))
        print(f"Response: {response}")
        return response
    print("No PROJECT configured")
    return JSONResponse({"error": "No PROJECT configured"}, status_code=400)

async def direct_event_function(request: Request, background_tasks: BackgroundTasks):
    """Direct EventGridTrigger function execution when PROJECT is set"""
    print("direct_event_function called")
    if loaded_function_info:
        # Use project and function_name to construct the full name
        function_full_name = f"{loaded_function_info.project}.{loaded_function_info.function_name}"
        print(f"Processing request for function: {function_full_name}")
        
        # Pass the PROJECT environment variable directly
        response = await event_proxy.proxy_function(request, os.getenv("PROJECT"), background_tasks=background_tasks)
        print(f"Response: {response}")
        return response
    print("No PROJECT configured")
    return JSONResponse({"error": "No PROJECT configured"}, status_code=400)