from fastapi import Request
from fastapi.responses import JSONResponse
import azure.functions as func
from proxy.base_proxy import BaseProxy
from LocalRunner.azure_request_type.http_request import AzureHttpRequest
from utils import parse_path_to_function_name, azure_response_to_fastapi

class APIProxy(BaseProxy):
    def __init__(self, request: Request, path: str):
        super().__init__(request, path)

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
        """Validate the HTTP request against the function info."""
        # Verify if the function is HTTP-triggered
        if not func_info.is_http():
            return JSONResponse(
                status_code=400,
                content={"error": f"Function '{func_info.function_name}' is not an HTTP-triggered function."}
            )

        # Verify if the method is allowed
        if self.request.method not in func_info.methods and "*" not in func_info.methods:
            return JSONResponse(
                status_code=405,
                content={"error": f"Method {self.request.method} not allowed for '{func_info.project}.{func_info.function_name}'. Allowed methods: {', '.join(func_info.methods)}"}
            )
        return None

    async def execution(self, func_info):
        """Execute the HTTP function."""
        # Create the AzureHttpRequest object
        body = await self.request.body()
        azure_request = AzureHttpRequest(self.request, body, func_info)
        await azure_request.setup()

        result = await super().execution(azure_request, func_info)
        if not isinstance(result, func.HttpResponse):
            return result
        return azure_response_to_fastapi(result)