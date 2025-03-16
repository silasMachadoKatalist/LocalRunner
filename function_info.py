import os
import sys
import importlib.util
from typing import Optional, List, Dict
from utils import load_function_json, get_http_methods, get_route

function_cache = {}
module_timestamps = {}

class FunctionInfo:
    def __init__(self, project: str, function_name: str, script_file: str, methods: List[str], route: Optional[str], function_dir: str):
        self.project = project
        self.function_name = function_name
        self.script_file = script_file
        self.methods = [m.upper() for m in methods]
        self.route = route
        self.function_dir = function_dir
        self.module = None
        
    def __str__(self):
        return f"{self.project}.{self.function_name} [{','.join(self.methods)}] -> {self.route or '/'}"
        
    def get_module_path(self):
        return os.path.join(self.function_dir, self.script_file)

def find_function_info(project: str, function_name: str, is_event: bool = False) -> Optional[FunctionInfo]:
    cache_key = f"{project}.{function_name}"
    if cache_key in function_cache:
        func_info = function_cache[cache_key]
        module_path = func_info.get_module_path()
        
        if module_path in module_timestamps:
            last_modified = os.path.getmtime(module_path)
            if last_modified > module_timestamps.get(module_path, 0):
                print(f"Detect change in file {module_path}, loading...")
                function_cache.pop(cache_key, None)
            else:
                return func_info
    
    base_dir = os.path.abspath(os.getcwd())
    function_dir = os.path.join(base_dir, project, function_name)
    
    if not os.path.exists(function_dir) or not os.path.isdir(function_dir):
        return None
    
    func_config = load_function_json(function_dir)
    if not func_config:
        return None
    
    # if not is_event and not is_http_function(func_config):
    #     return None
    
    script_file = func_config.get("scriptFile", "")
    if not script_file:
        for file in os.listdir(function_dir):
            if file.endswith(".py"):
                script_file = file
                break
                
    if not script_file:
        return None
    
    methods = get_http_methods(func_config) if not is_event else []
    route = get_route(func_config, function_name) if not is_event else None
    
    func_info = FunctionInfo(
        project=project,
        function_name=function_name,
        script_file=script_file,
        methods=methods,
        route=route,
        function_dir=function_dir
    )
    
    function_cache[cache_key] = func_info
    
    print(f"Function found: {func_info}")
    return func_info

def load_function_module(func_info: FunctionInfo) -> bool:
    file_path = os.path.join(func_info.function_dir, func_info.script_file)
    if not os.path.exists(file_path):
        print(f"Script file not found: {file_path}")
        return False
        
    try:
        module_name = os.path.splitext(func_info.script_file)[0]
        
        module_timestamps[file_path] = os.path.getmtime(file_path)
        
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        sys.path.insert(0, func_info.function_dir)
        sys.path.insert(0, os.path.dirname(func_info.function_dir))
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return False
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        module.__package__ = func_info.function_name
        
        spec.loader.exec_module(module)
        
        sys.path.pop(0)
        sys.path.pop(0)
        
        if hasattr(module, "main") and callable(module.main):
            func_info.module = module
            return True
        else:
            print(f"Module {module_name} is missing function 'main'")
            return False
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error loading module {func_info.script_file}: {e}")
        return False

def monitor_submodules(func_info: FunctionInfo):
    for root, _, files in os.walk(func_info.function_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                last_modified = os.path.getmtime(file_path)
                if file_path not in module_timestamps or last_modified > module_timestamps[file_path]:
                    print(f"Detect change in file {file_path}, loading...")
                    module_timestamps[file_path] = last_modified
                    if func_info.module:
                        del sys.modules[func_info.module.__name__]
                    load_function_module(func_info)
    
    shared_libraries_dir = os.path.join(os.path.abspath(os.getcwd()), 'SharedLibraries')
    for root, _, files in os.walk(shared_libraries_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                last_modified = os.path.getmtime(file_path)
                if file_path not in module_timestamps or last_modified > module_timestamps[file_path]:
                    print(f"Detect change in file {file_path}, loading...")
                    module_timestamps[file_path] = last_modified
                    if func_info.module:
                        del sys.modules[func_info.module.__name__]
                    load_function_module(func_info)

class AzureFunctionContext:
    def __init__(self, function_directory: str, function_name: str):
        self.function_directory = function_directory
        self.function_name = function_name
        self.invocation_id = "local-debug-id"