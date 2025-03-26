import os
import sys
from context_execution_singleton import ContextExecutionSingleton as executor

class BaseEnvironmentSetup:
    def __init__(self):
        # Watch everything except ignored directories
        self.root_dir = os.getcwd()
        
        projects_to_ignore = os.getenv("PROJECTS_TO_IGNORE", "").split(",")
        self.directories_to_watch = [
            os.path.join(self.root_dir, d) for d in os.listdir(self.root_dir)
            if os.path.isdir(os.path.join(self.root_dir, d)) and d not in ["LocalRunner"] + projects_to_ignore
        ]
    """Base class for environment setup."""

    def setup_environment(self):
        """Configure the environment to run Azure Functions locally"""
        
        if self.root_dir not in sys.path:
            sys.path.insert(0, self.root_dir)
        
        print(f"Environment configured with root directory: {self.root_dir}")
        
    def setup_executor(self):
        """Configure the executor"""
        print(f"Setupping Executor")
        
    def setup_file_watcher(self):
        print(f"Setupping File watcher")
        from threading import Thread
        from file_watcher import start_file_watcher
        # Start the file watcher
        watcher_thread = Thread(target=start_file_watcher, args=(self.directories_to_watch, executor))
        watcher_thread.daemon = True
        watcher_thread.start()
        folder_names = [os.path.basename(directory) for directory in self.directories_to_watch]
        print(f"File watcher started for directories: {folder_names}")

class DynamicEnvironmentSetup(BaseEnvironmentSetup):
    """Environment setup for dynamic mode"""
    pass
    
class ProjectEnvironmentSetup(BaseEnvironmentSetup):
    def setup_file_watcher(self):
        """Start a file watcher to reload modules on changes"""
        project = os.getenv("PROJECT")
        extra_projects_to_track = os.getenv("EXTRA_PROJECTS_TO_TRACK", "").split(",")

        if project:
            # Watch only the project_dir and SharedLibraries
            try:
                self.directories_to_watch = [
                    os.path.join(self.root_dir, project),
                    os.path.join(self.root_dir, "SharedLibraries")
                ]
                # Add extra directories to track
                self.directories_to_watch.extend(
                    [os.path.join(self.root_dir, extra.strip()) for extra in extra_projects_to_track if extra.strip()]
                )
            except ValueError:
                print("Invalid PROJECT: #{project} to watch")
                self.directories_to_watch = []
            super().setup_file_watcher()

class ProjectFunctionEnvironmentSetup(ProjectEnvironmentSetup):
    def setup_executor(self):
        super().setup_executor()
        project = os.getenv("PROJECT")
        function = os.getenv("FUNCTION")
        if project and function:
            try:
                executor.load(
                    project_dir=project,
                    main_module=function
                )
                print(f"Executor loaded for PROJECT.FUNCTION: {project}.{function}")
            except ValueError:
                print("Invalid PROJECT.FUNCTION format. Expected 'ProjectDir.MainModule'")
        else:
            print("PROJECT and FUNCTION is not set. Skipping executor load.")
