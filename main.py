import os
from threading import Thread
from file_watcher import start_file_watcher
import uvicorn
from context_execution_singleton import ContextExecutionSingleton

if __name__ == "__main__":
    project = os.getenv("PROJECT")
    function = os.getenv("FUNCTION")
    port = int(os.getenv("PORT", 3000))  # Default to port 3000 if PORT is not set
    workspace_folder = os.getenv("PYTHONPATH", os.getcwd())  # Use PYTHONPATH as the workspace folder
    print(f"Workspace Folder: {workspace_folder}")

    app_starter = None
    if project and function:
        app_starter = "project_function_app:app"
    elif project:
        app_starter = "project_app:app"
    else:
        app_starter = "dynamic_app:app"

    print("Await for the application to start...")
    uvicorn.run(
        app_starter,
        host="0.0.0.0",
        port=port
    )