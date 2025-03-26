import os
import json
from typing import Dict, Any, Optional, List
from fastapi import Response
import azure.functions as func

def parse_path_to_function_name(path: str) -> tuple:
    parts = path.strip('/').split('/')
    if not parts or len(parts) < 1:
        return None, None, []
        
    if '.' in parts[0]:
        project, function = parts[0].split('.', 1)
        remaining_path = parts[1:] if len(parts) > 1 else []
        return project, function, remaining_path
        
    if len(parts) >= 2:
        project = parts[0]
        function = parts[1]
        remaining_path = parts[2:] if len(parts) > 2 else []
        return project, function, remaining_path
        
    return parts[0], None, []

def load_function_json(function_path: str) -> Optional[Dict[str, Any]]:
    json_path = os.path.join(function_path, "function.json")
    if not os.path.exists(json_path):
        return None
        
    with open(json_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def extract_route_params(route_template: str, path_parts: List[str]) -> Dict[str, str]:
    if not route_template:
        return {}
        
    template_parts = route_template.split('/')
    
    if len(template_parts) > len(path_parts):
        return {}
    
    params = {}
    for i, template in enumerate(template_parts):
        if i < len(path_parts) and template.startswith('{') and template.endswith('}'):
            param_name = template[1:-1]
            params[param_name] = path_parts[i]
    
    return params

def azure_response_to_fastapi(azure_response: func.HttpResponse) -> Response:
    headers = {}
    for key, value in azure_response.headers.items():
        headers[key] = value
        
    return Response(
        content=azure_response.get_body(),
        status_code=azure_response.status_code,
        headers=headers,
        media_type=azure_response.mimetype
    )
