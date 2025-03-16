from fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse
from azure.functions import HttpResponse

from function_info import FunctionInfo, load_function_module, monitor_submodules, AzureFunctionContext
from utils import extract_route_params, azure_response_to_fastapi

class BaseProxy:
    async def execute_function(self, func_info: FunctionInfo, request_obj):
        """Executa uma função"""
        try:
            result = func_info.module.main(request_obj)
            
            if isinstance(result, HttpResponse):
                return azure_response_to_fastapi(result)
            else:
                return JSONResponse(content={"result": str(result)})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"error": f"Execução da função falhou: {str(e)}"}
            )

    async def proxy_function(self, request: Request, function_path: str, is_event: bool, background_tasks: BackgroundTasks = None):
        """Função principal que faz proxy de requisições para Azure Functions"""
        from function_info import find_function_info
        from utils import parse_path_to_function_name

        project, function_name, remaining_path = parse_path_to_function_name(function_path)
        
        if not project or not function_name:
            return JSONResponse(
                status_code=400,
                content={"error": f"Path inválido: '{function_path}'. Use o formato Projeto.Função ou Projeto/Função"}
            )
        
        func_info = find_function_info(project, function_name)
        if not func_info:
            return JSONResponse(
                status_code=404,
                content={"error": f"Função '{project}.{function_name}' não encontrada ou não é uma função HTTP"}
            )
        
        if not is_event and request.method not in func_info.methods and "*" not in func_info.methods:
            return JSONResponse(
                status_code=405,
                content={"error": f"Método {request.method} não permitido para '{function_path}'. Métodos permitidos: {', '.join(func_info.methods)}"}
            )
            
        monitor_submodules(func_info)
        
        if not func_info.module and not load_function_module(func_info):
            return JSONResponse(
                status_code=500,
                content={"error": f"Não foi possível carregar o módulo da função para '{function_path}'"}
            )
        
        route_params = {}
        if func_info.route:
            route_params = extract_route_params(func_info.route, remaining_path)
        
        context = AzureFunctionContext(func_info.function_dir, func_info.function_name)
        
        return func_info, route_params, context