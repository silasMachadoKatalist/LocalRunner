import os
import sys
import importlib
from contextlib import contextmanager

class ContextExecutionSingleton:
    _pool = {}  # Pool de instâncias, identificadas por (project_dir, main_module)
    
    def __init__(self, project_dir, main_module, should_log=False):
        self.project_dir = project_dir
        self.main_module_name = main_module
        self.should_log = should_log

        try:
            with self.change_directory(self.project_dir):
                self.main_module = importlib.import_module(main_module)
        except ImportError as e:
            print(f"Error initializing module: {e}")
            self.main_module = None

    @staticmethod
    @contextmanager
    def change_directory(destination):
        original_directory = os.getcwd()
        absolute_path = os.path.abspath(destination)  # Retrieve the absolute path for the directory
        sys.path.insert(0, absolute_path)  # Add directory to sys.path
        os.chdir(absolute_path)
        try:
            yield
        finally:
            os.chdir(original_directory)
            sys.path.pop(0)  # Remove directory from sys.path after use

    def refresh_module(self, module_name):
        """Refresh a specific module."""
        
        # Remove project_dir from module_name if it exists
        if module_name.startswith(self.project_dir.replace(os.sep, '.')):
            module_name = module_name[len(self.project_dir.replace(os.sep, '.')) + 1:]
        with self.change_directory(self.project_dir):
            try:
                module = importlib.import_module(module_name)
                return importlib.reload(module)
            except ImportError as e:
                if self.should_log:
                    print(f"Error reloading module {module_name}: {e}")
                return None

    def execute(self, azure_request):
        """Execute the main function for the module."""
        with self.change_directory(self.project_dir):
            try:
                module = importlib.import_module(self.main_module_name)
                importlib.reload(module)

                main = getattr(module, "main")
                return main(azure_request)
            except ModuleNotFoundError as e:
                raise Exception(f"Module not found: {e}")
            except AttributeError as e:
                raise Exception(f"Function 'main' not found in module: {e}")

    @classmethod
    def load(cls, project_dir: str, main_module: str):
        """Load an instance from the pool or create a new one."""
        key = (project_dir, main_module)
        if key not in cls._pool:
            cls._pool[key] = cls(project_dir, main_module)
        return cls._pool[key]

    @classmethod
    def refresh_module_for_all_executors(cls, module_name):
        """Call refresh_module on all instances in the pool with the given module name."""
        for inst in cls._pool.values():
            inst.refresh_module(module_name)