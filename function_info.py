import os
from typing import Optional, List, Dict, Any
from enum import Enum
from utils import load_function_json

class TYPE(Enum):
    HTTP = "json"
    EVENT = "python_file"
    
class FunctionInfo:
    def __init__(self, project: str, function_name: str, script_file: str, methods: List[str], route: Optional[str], function_dir: str, type: str):
        self.project = project
        self.function_name = function_name
        self.script_file = script_file
        self.methods = [m.upper() for m in methods]
        self.route = route
        self.function_dir = function_dir
        self.type = type

    def __str__(self):
        return f"{self.project}.{self.function_name} [{','.join(self.methods)}] -> {self.route or '/'}"
    
    def is_http(self) -> bool:
        return self.type == TYPE.HTTP
    
    def is_event(self) -> bool:
        return self.type == TYPE.EVENT

def get_http_methods(function_config: Dict[str, Any]) -> List[str]:
    for binding in function_config["bindings"]:
        if binding.get("type", "").lower() == "httptrigger":
            methods = binding.get("methods", ["GET"])
            return [m.upper() for m in methods]
    return ["GET"]

def get_route(function_config: Dict[str, Any], function_name: str) -> Optional[str]:
    for binding in function_config["bindings"]:
        if binding.get("type", "").lower() == "httptrigger":
            if "route" in binding:
                return binding["route"]
    return None

def get_type(function_config: Dict[str, Any]) -> str:
    for binding in function_config["bindings"]:
        binding_type = binding.get("type", "").lower()
        if binding_type == "httptrigger":
            return TYPE.HTTP
        elif binding_type == "eventgridtrigger":
            return TYPE.EVENT
        return None

def find_function_info(project: str, function_name: str) -> Optional[FunctionInfo]:
    """Find and prepare the function info for a given project and function."""
    base_dir = os.path.abspath(os.getcwd())
    project_dir = os.path.join(base_dir, project)

    if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
        print(f"Project directory not found: {project_dir}")
        return None

    function_dir = os.path.join(project_dir, function_name)
    if not os.path.exists(function_dir) or not os.path.isdir(function_dir):
        print(f"Function directory not found: {function_dir}")
        return None

    func_config = load_function_json(function_dir)
    if not func_config:
        print(f"Function configuration not found in: {function_dir}")
        return None

    script_file = func_config.get("scriptFile", "")
    if not script_file:
        for file in os.listdir(function_dir):
            if file.endswith(".py"):
                script_file = file
                break

    if not script_file:
        print(f"No script file found in function directory: {function_dir}")
        return None

    methods = get_http_methods(func_config)
    route = get_route(func_config, function_name)
    type = get_type(func_config)

    return FunctionInfo(
        project=project,
        function_name=function_name,
        script_file=script_file,
        methods=methods,
        route=route,
        function_dir=function_dir,
        type=type
    )