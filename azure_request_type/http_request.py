import re
import json
from typing import Dict, Any
from fastapi import Request
import azure.functions as func

def transform_url(url: str) -> str:
    pattern = re.compile(r'(https?://)?([^/]+)/(api)/([^/]+)\.([^/]+)/')
    return re.sub(pattern, r'\1\2/\3/', url)

def extract_params(mask: str, url: str) -> dict:
    # Extraindo os nomes dos parâmetros
    mask_parts = mask.split('/')
    param_names = [part.strip('{}') for part in mask_parts if part.startswith('{') and part.endswith('}')]
    
    # Removendo query parameters
    url_base = url.split('?')[0]
    
    # Separando os segmentos da URL
    url_parts = url_base.split('/')
    
    # Encontrando o ponto de início dos parâmetros na URL
    start_index = next((i for i, part in enumerate(url_parts) if part in mask_parts), len(url_parts) - len(param_names))
    
    # Pegando os valores correspondentes aos parâmetros
    param_values = url_parts[start_index:start_index + len(param_names)]
    
    return dict(zip(param_names, param_values))

class AzureHttpRequest(func.HttpRequest):
    def __init__(self, request: Request, body: bytes, func_info=None):
        self._request = request
        self._body = body
        self._body_bytes = body
        self._params = {}
        self._headers = {}
        self._route_params = {}
        self._func_info = func_info  # Adiciona o func_info para processar o route
        self._url = str(self._request.url)  # Inicializa a URL original

    async def setup(self):
        """Config Azure request from fastapi."""
        self._params = dict(self._request.query_params)
        self._headers = dict(self._request.headers)
        if not self._body:
            self._body = await self._request.body()
            self._body_bytes = self._body

        # process URL prefix /api/{func_info.project}.{func_info.function_name} if exists
        if self._func_info:
            self._url = transform_url(self._url)

            # Process route_params if route is defined
            if self._func_info.route:
                self._route_params = extract_params(self._func_info.route, self._url)

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
    
    def get_json(self) -> Any:
        return json.loads(self._body.decode('utf-8'))