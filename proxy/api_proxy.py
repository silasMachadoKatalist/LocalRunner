from fastapi import Request, BackgroundTasks
from proxy.base_proxy import BaseProxy
from LocalRunner.azure_request_type.http_request import HttpRequest

class APIProxy(BaseProxy):
    async def proxy_function(self, request: Request, function_path: str, is_event: bool = False, background_tasks: BackgroundTasks = None):
        func_info, route_params, context = await super().proxy_function(request, function_path, is_event, background_tasks)
        
        body = await request.body()
        azure_request = HttpRequest(request, body, route_params)
        await azure_request.setup()
        
        return await self.execute_function(func_info, azure_request)