from fastapi import Request
from fastapi.responses import JSONResponse
from function_info import FunctionInfo, find_function_info
from context_execution_singleton import ContextExecutionSingleton as executor

class BaseProxy:
    def __init__(self, request: Request, path: str):
        self.request = request
        self.path = path

    async def proxy_function(self):
        """Main proxy function to handle the request."""
        # Load function info
        func_info = await self.load_function_info(self.path)
        if isinstance(func_info, JSONResponse):  # If load_function_info returns an error
            return func_info

        # Validate the request
        validation_error = await self.validate(func_info)
        if validation_error:
            return validation_error

        # Execute the function
        return await self.execution(func_info)

    async def load_function_info(self, function_path: str) -> FunctionInfo:
        """Load the function info based on the function path."""
        func_info = find_function_info(function_path.split(".")[0], function_path.split(".")[1])
        if not func_info:
            return JSONResponse(
                status_code=404,
                content={"error": f"Function '{function_path}' not found"}
            )
        return func_info

    async def validate(self, func_info: FunctionInfo) -> JSONResponse:
        """Validate the request against the function info."""
        # This method is intentionally left blank for subclasses to implement specific validations
        return None

    async def execution(self, azure_request, func_info: FunctionInfo):
        """Execute the function."""
        # Create the Azure Function context
        try:
            return executor.load(
                project_dir=func_info.project,
                main_module=f"{func_info.function_name}.{func_info.script_file}".removesuffix(".py")
            ).execute(azure_request)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"error": f"Function execution failed: {str(e)}"}
            )