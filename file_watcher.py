from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from context_execution_singleton import ContextExecutionSingleton
import os

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, executor: ContextExecutionSingleton = ContextExecutionSingleton, should_log: bool = False):
        self.executor = executor
        self.should_log = should_log

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return

        if self.should_log:
            print(f"Detected modification in: {event.src_path}")

        self.reload_module_and_dependencies(event.src_path)

    def on_created(self, event):
        if not event.src_path.endswith(".py"):
            return

        if self.should_log:
            print(f"Detected new file: {event.src_path}")
            
        self.reload_module_and_dependencies(event.src_path)

    def reload_module_and_dependencies(self, file_path):
        if "_cache_" in file_path:
            if self.should_log:
                print(f"Skipping cache file: {file_path}")
            return
        
        # format the path to be imported
        project_root = os.getcwd().replace("\\", "/")
        formatted_path = file_path.replace("\\", "/").replace(project_root + "/", "")
        formatted_path = formatted_path.replace("/", ".").rsplit(".py", 1)[0]
        self.executor.refresh_module_for_all_executors(formatted_path)

def start_file_watcher(directories_to_watch, executor):
    if not directories_to_watch:
        print("No directories to watch. File watcher will not start.")
        return

    event_handler = FileChangeHandler(executor)
    observer = Observer()
    for directory in directories_to_watch:
        if os.path.exists(directory):
            observer.schedule(event_handler, path=directory, recursive=True)
        else:
            print(f"Directory does not exist and will be skipped: {directory}")

    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()