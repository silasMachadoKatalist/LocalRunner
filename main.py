import uvicorn
import os

if __name__ == "__main__":
    project = os.getenv("PROJECT")
    port = int(os.getenv("PORT", 3000))  # Default to port 3000 if PORT is not set

    if project:
        # Start the app in project mode
        print(f"Starting in Project Mode with PROJECT={project}")
        uvicorn.run("project_app:app", host="0.0.0.0", port=port, reload=True)
    else:
        # Start the app in dynamic mode
        print("Starting in Dynamic Mode")
        uvicorn.run("dynamic_app:app", host="0.0.0.0", port=port, reload=True)