import asyncio
from fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse
from proxy.base_proxy import BaseProxy
from LocalRunner.azure_request_type.event_request import EventRequest

class EventProxy(BaseProxy):
    async def proxy_function(self, request: Request, function_path: str, is_event: bool = True, background_tasks: BackgroundTasks = None):
        result = await super().proxy_function(request, function_path, is_event, background_tasks)
        
        if isinstance(result, JSONResponse):
            return result
        
        func_info, route_params, context = result
        
        body = await request.json()
        event_request = EventRequest(body)
        
        async_header = request.headers.get("async", "false").lower()
        timeout_header = request.headers.get("timeout", "300")
        try:
            timeout = int(timeout_header)
        except ValueError:
            timeout = 300  # Default to 5 minutes if the header is not a valid integer
        
        if async_header == "true":
            background_tasks.add_task(self.execute_function_with_timeout, func_info, event_request, timeout)
            return JSONResponse(content={"status": "accepted"}, status_code=202)
        else:
            await self.execute_function_with_timeout(func_info, event_request, timeout)
            return JSONResponse(content={"status": "accepted"}, status_code=202)

    async def execute_function_with_timeout(self, func_info, event_request, timeout=300):
        """Execute function with a timeout"""
        try:
            await asyncio.wait_for(self.execute_function(func_info, event_request), timeout)
        except asyncio.TimeoutError:
            print(f"Execution of function {func_info.function_name} exceeded the time limit of {timeout} seconds")