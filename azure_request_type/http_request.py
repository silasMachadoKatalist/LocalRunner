from typing import Dict
from fastapi import Request
import azure.functions as func

class HttpRequest(func.HttpRequest):
    def __init__(self, request: Request, body: bytes, route_params: Dict[str, str] = None):
        self._request = request
        self._body = body
        self._params = {}
        self._headers = {}
        self._route_params = route_params or {}
        
    async def setup(self):
        self._params = dict(self._request.query_params)
        self._headers = dict(self._request.headers)
        if not self._body:
            self._body = await self._request.body()
        
    @property
    def method(self) -> str:
        return self._request.method
        
    @property
    def url(self) -> str:
        return str(self._request.url)
        
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