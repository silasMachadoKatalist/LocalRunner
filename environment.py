import os
import sys

def setup_environment():
    """Configure the environment to run Azure Functions locally"""
    root_dir = os.path.abspath(os.getcwd())
    
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    shared_libraries_dir = os.path.join(root_dir, 'SharedLibraries')
    if shared_libraries_dir not in sys.path:
        sys.path.insert(0, shared_libraries_dir)
    
    print(f"Environment configured with root directory: {root_dir}")
    print(f"SharedLibraries configured with directory: {shared_libraries_dir}")