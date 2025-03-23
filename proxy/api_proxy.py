from fastapi import Request
from fastapi.responses import JSONResponse
from proxy.base_proxy import BaseProxy
from LocalRunner.azure_request_type.http_request import AzureHttpRequest
from utils import extract_route_params, parse_path_to_function_name

class APIProxy(BaseProxy):
    def __init__(self, request: Request, path: str):
        super().__init__(request, path)
        self.remaining_path = ""  # Variável para armazenar o restante do path

    async def load_function_info(self, function_path: str):
        """Load the function info and extract the remaining path."""
        # Usar parse_path_to_function_name para separar o path
        project, function_name, remaining_path = parse_path_to_function_name(function_path)
        if not project or not function_name:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid Path: '{function_path}'. Use the format Project.Function"}
            )

        # Salvar o restante do path na instância
        self.remaining_path = "/".join(remaining_path)

        # Chamar o método original para carregar as informações da função
        return await super().load_function_info(f"{project}.{function_name}")

    async def validate(self, func_info):
        """Validate the HTTP request against the function info."""
        # Verificar se a função é do tipo HTTP
        if not func_info.is_http():
            return JSONResponse(
                status_code=400,
                content={"error": f"Function '{func_info.function_name}' is not an HTTP-triggered function."}
            )

        # Verificar se o método HTTP é permitido
        if self.request.method not in func_info.methods and "*" not in func_info.methods:
            return JSONResponse(
                status_code=405,
                content={"error": f"Method {self.request.method} not allowed for '{func_info.project}.{func_info.function_name}'. Allowed methods: {', '.join(func_info.methods)}"}
            )
        return None

    async def execution(self, func_info):
        """Execute the HTTP function."""
        # Extrair parâmetros de rota
        route_params = {}
        if func_info.route:
            route_params = extract_route_params(func_info.route, self.request.url.path.split("/")[2:])

        # Adicionar o restante do path como um parâmetro
        if self.remaining_path:
            route_params["remaining_path"] = self.remaining_path

        # Criar o objeto HttpRequest
        body = await self.request.body()
        azure_request = AzureHttpRequest(self.request, body, func_info)
        await azure_request.setup()

        # Executar a função
        return await super().execution(azure_request, func_info)