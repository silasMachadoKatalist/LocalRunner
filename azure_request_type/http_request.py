from typing import Dict, List
from fastapi import Request
import azure.functions as func

def extract_route_params(route_template: str, path_parts: List[str]) -> Dict[str, str]:
    """Extrai os parâmetros da rota com base no template e no caminho."""
    route_params = {}
    route_segments = route_template.split("/")
    for i, segment in enumerate(route_segments):
        if segment.startswith("{") and segment.endswith("}"):
            param_name = segment.strip("{}").rstrip("?")
            is_optional = segment.endswith("?")
            if i < len(path_parts):
                route_params[param_name] = path_parts[i]
            elif not is_optional:
                # Parâmetro obrigatório ausente
                route_params[param_name] = None
    return route_params

class AzureHttpRequest(func.HttpRequest):
    def __init__(self, request: Request, body: bytes, func_info=None):
        self._request = request
        self._body = body
        self._params = {}
        self._headers = {}
        self._route_params = {}
        self._func_info = func_info  # Adiciona o func_info para processar o route
        self._url = str(self._request.url)  # Inicializa a URL original

    async def setup(self):
        """Configura os parâmetros do request e sobrescreve a URL."""
        self._params = dict(self._request.query_params)
        self._headers = dict(self._request.headers)
        if not self._body:
            self._body = await self._request.body()

        # Processar a URL para remover o prefixo /api/{func_info.project}.{func_info.function_name}
        if self._func_info:
            original_path = self._request.url.path
            prefix = f"/api/{self._func_info.project}.{self._func_info.function_name}"
            if original_path.startswith(prefix):
                # Remover o prefixo da URL
                remaining_path = original_path[len(prefix):].lstrip("/")
            else:
                remaining_path = original_path.lstrip("/")

            # Processar os route_params com base no func_info.route
            if self._func_info.route:
                # Remover o prefixo da rota base, se existir
                route_base = self._func_info.route.split("/")[0]
                if remaining_path.startswith(route_base):
                    remaining_path = remaining_path[len(route_base):].lstrip("/")
                # Extrair os parâmetros da rota
                self._route_params = extract_route_params(self._func_info.route, remaining_path.split("/"))

            # Atualizar a URL para refletir o caminho processado
            self._url = f"/{remaining_path}"
            if self._params:
                # Adicionar os parâmetros de consulta (query params) de volta à URL
                query_string = "&".join([f"{key}={value}" for key, value in self._params.items()])
                self._url = f"{self._url}?{query_string}"

    @property
    def method(self) -> str:
        return self._request.method

    @property
    def url(self) -> str:
        return self._url  # Retorna a URL processada

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def params(self) -> Dict[str, str]:
        return self._params

    @property
    def route_params(self) -> Dict[str, str]:
        return self._route_params

    @property
    def body(self) -> bytes:
        return self._body