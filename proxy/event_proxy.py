import asyncio
from fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse
from proxy.base_proxy import BaseProxy
from LocalRunner.azure_request_type.event_request import EventRequest
from utils import parse_path_to_function_name

class EventProxy(BaseProxy):
    def __init__(self, request: Request, path: str, background_tasks: BackgroundTasks = None):
        super().__init__(request, path)
        self.background_tasks = background_tasks
        
    async def load_function_info(self, function_path: str):
        """Load the function info and extract the remaining path."""
        # Usar parse_path_to_function_name para separar o path
        project, function_name, remaining_path = parse_path_to_function_name(function_path)
        if not project or not function_name:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid Path: '{function_path}'. Use the format Project.Function"}
            )

        return await super().load_function_info(f"{project}.{function_name}")
    
    async def validate(self, func_info):
        """Validate the Event request against the function info."""
        # Verify if the function is Event-triggered
        if not func_info.is_event():
            return JSONResponse(
                status_code=400,
                content={"error": f"Function '{func_info.function_name}' is not an Event-triggered function."}
            )
        return None

    async def execution(self, func_info):
        """Execute the Event function."""
        body = await self.request.json()

        if not isinstance(body, list):
            return JSONResponse(
                status_code=400,
                content={"error": "Request body must be a list."}
            )

        sync_header = self.request.headers.get("sync", "false").lower()
        timeout_header = self.request.headers.get("timeout", "300")
        try:
            timeout = int(timeout_header)
        except ValueError:
            timeout = 300  # Default to 5 minutes if the header is not a valid integer

        if sync_header == "true":
            return await self._execute_sync_mode(func_info, body, timeout)
        else:
            return await self._execute_async_mode(func_info, body, timeout)

    async def _execute_sync_mode(self, func_info, body, timeout):
        """Execute function in synchronous mode."""
        # Synchronous mode: only allow a single item in the list
        if len(body) != 1:
            return JSONResponse(
                status_code=400,
                content={"error": "Synchronous mode only supports a list with exactly one item."}
            )

        event_request = EventRequest(body[0])
        await self.execute_function_with_timeout(event_request, func_info, timeout)
        return JSONResponse(content=[{"status": "completed"}], status_code=200)
        
    async def _execute_async_mode(self, func_info, body, timeout):
        """Execute function in asynchronous mode."""
        
        tasks = []
        for item in body:
            event_request = EventRequest(item)
            task = asyncio.create_task(
            self.execute_function_with_timeout(event_request, func_info, timeout)
            )
            tasks.append(task)
        
        # Return immediately with a simple acceptance response
        return JSONResponse(
            content={"status": "accepted" }, 
            status_code=200
        )
        
    async def execute_function_with_timeout(self, event_request, func_info, timeout=300):
        """Execute function with a timeout."""
        try:
            asyncio.create_task(
                asyncio.wait_for(super().execution(event_request, func_info), timeout)
            )
        except asyncio.TimeoutError:
            print(f"Execution of function {func_info.function_name} exceeded the time limit of {timeout} seconds")
        except Exception as e:
            print(f"Unexpected error in function {func_info.function_name}: {e}")