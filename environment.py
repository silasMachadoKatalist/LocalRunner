import os
import sys
from context_execution_singleton import ContextExecutionSingleton as executor

def setup_environment():
    """Configure the environment to run Azure Functions locally"""
    root_dir = os.path.abspath(os.getcwd())
    
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    print(f"Environment configured with root directory: {root_dir}")

def setup_executor():
    """Load the executor for the PROJECT_FUNCTION"""
    print(f"Setupping Executor")
    project_function = os.getenv("PROJECT_FUNCTION")
    if project_function:
        try:
            project_dir, main_module = project_function.split(".", 1)
            executor.load(
                project_dir=project_dir,
                main_module=main_module
            )
            print(f"Executor loaded for PROJECT_FUNCTION: {project_function}")
        except ValueError:
            print("Invalid PROJECT_FUNCTION format. Expected 'ProjectDir.MainModule'")
    else:
        print("PROJECT_FUNCTION is not set. Skipping executor load.")

def setup_file_watcher():
    """Start a file watcher to reload modules on changes"""
    from threading import Thread
    from file_watcher import start_file_watcher
    print(f"Setupping File watcher")

    # Determine directories to watch
    root_dir = os.getcwd()
    project_function = os.getenv("PROJECT_FUNCTION")
    projects_to_ignore = os.getenv("PROJECTS_TO_IGNORE", "").split(",")
    extra_projects_to_track = os.getenv("EXTRA_PROJECTS_TO_TRACK", "").split(",")

    if project_function:
        # Watch only the project_dir and SharedLibraries
        try:
            project_dir, _ = project_function.split(".", 1)
            directories_to_watch = [
                os.path.join(root_dir, project_dir),
                os.path.join(root_dir, "SharedLibraries")
            ]
            # Add extra directories to track
            directories_to_watch.extend(
                [os.path.join(root_dir, extra.strip()) for extra in extra_projects_to_track if extra.strip()]
            )
        except ValueError:
            print("Invalid PROJECT_FUNCTION format. Expected 'ProjectDir.MainModule'")
            directories_to_watch = []
    else:
        # Watch everything except ignored directories
        directories_to_watch = [
            os.path.join(root_dir, d) for d in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, d)) and d not in ["LocalRunner"] + projects_to_ignore
        ]

    # Start the file watcher
    watcher_thread = Thread(target=start_file_watcher, args=(directories_to_watch, executor))
    watcher_thread.daemon = True
    watcher_thread.start()
    folder_names = [os.path.basename(directory) for directory in directories_to_watch]
    print(f"File watcher started for directories: {folder_names}")