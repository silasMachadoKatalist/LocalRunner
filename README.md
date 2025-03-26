# Local Azure Functions Proxy

This project provides a local proxy for Azure Functions, allowing you to test and debug your Azure Functions locally using FastAPI. The proxy supports both HTTP-triggered functions and EventGrid-triggered functions. Additionally, it supports hot reload, enabling you to see changes in real-time without restarting the server. Dependencies are dynamically loaded on the first request, ensuring that the latest versions are always used.

# Why This Project Was Created
This project was created to provide a local development environment for Azure Functions, allowing developers to test and debug their functions locally before deploying them to Azure. The main reason for this project is due to the structure we have, where everything runs from the root of the project, and our pipeline needs to copy the ShareLibraries folder into the function's context. Additionally, we are unable to run Azurite locally due to the way the project is structured. By using FastAPI as a proxy, developers can easily simulate HTTP and EventGrid triggers and ensure their functions behave as expected.

# Install dependencies:
```sh
pip install -r requirements.txt
```

# Modes

This project is designed to be used in three different ways.  
The recommended approach is **Project Mode**.  
The activation of each mode depends on whether the `PROJECT` and `FUNCTION` environment variables are declared..

### **Notes**  
1. All startup modes listed here use VS Code debugger configurations, but you can also run them locally from the terminal if preferred.  
2. You must run the project from the same folder structure as your other projects. If you clone this project alongside the rest, it should work properly.

<br>

**Shared envs**:
| env | description | sample |
| ----| ------ | ------ |
|PORT| The application port that will be used on your machine.| 3000 |

## Dynamic

This mode provides access to all projects and functions simultaneously.  
It is useful for quickly executing an HTTP request or event that does not trigger another event or request.  
If you need to chain events or requests in your calls, please run a second instance of the application or start it in **Project Mode**.

**Especific envs:**
| env | description | sample |
| ----| ------ | ------ |
|PROJECTS_TO_IGNORE| A comma-separated string array of folders that you want to ignore. | project1,project2 |

### How to run

```json
{
  "name": "Local Azure Functions Proxy - Dynamic",
  "type": "debugpy",
  "request": "launch",
  "program": "${workspaceFolder}/LocalRunner/main.py",
  "console": "integratedTerminal",
  "justMyCode": false,
  "internalConsoleOptions": "neverOpen",
  "env": {
      "PYTHONPATH": "${workspaceFolder}",
      "PORT": "3000",
      "PROJECTS_TO_IGNORE": ".pytest_cache,.vscode,allure-results,test_scripts,__blobstorage__,__queuestorage__,Test_Framework",
      "ENV_PATH": ".env",
      "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
      "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
      "USE_LOCAL_EVENT_EMITTER": "true",
  }
}       
```

## Project

This mode is the most recommended to run, as it closely resembles the Azure FunctionApp. Functions under this domain can share memory context.  
Another advantage is that hot reload and the context loader will only look for shared libraries and your chosen API.

**Especific envs:**
| env | description | sample |
| ----| ------ | ------ |
|PROJECT| The folder/module name of your project | File |

### How to run
```json
{
    "name": "Start File",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/LocalRunner/main.py",
    "console": "integratedTerminal",
    "justMyCode": false,
    "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PORT": "3001",
        "PROJECT": "File",
        "ENV_PATH": ".env",
        "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_EVENT_EMITTER": "true",
        "KT_DEV_EXEC_MAPPING_CODE_TOPIC_ENDPOINT": "http://localhost:3002/event/CodeExecEvent",
    }
}
```

You can also use compounds to start multiple applications at once.  
Each one will log into different terminals and debugger contexts.

```json
{
  "configurations": [
    {
      "name": "Start File",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/LocalRunner/main.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PORT": "3001",
        "PROJECT": "File",
        "ENV_PATH": ".env",
        "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_EVENT_EMITTER": "true",
        "KT_DEV_EXEC_MAPPING_CODE_TOPIC_ENDPOINT": "http://localhost:3002/event/CodeExecEvent",
      }
    },
    {
      "name": "Start Utils",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/LocalRunner/main.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
          "PYTHONPATH": "${workspaceFolder}",
          "PORT": "3002",
          "PROJECT": "Utils",
          "ENV_PATH": ".env",
          "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
          "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
          "USE_LOCAL_EVENT_EMITTER": "true",
      }
    }
  ],
  "compounds": [
    {
      "name": "Start Utils + File",
      "configurations": ["Start Utils", "Start File"]
    }
  ]
}
```
## Function

This mode is designed to load the context for a single function only. Since sometimes the function acts as a standalone API, it is helpful when you have requests and events that trigger actions within the same project, preventing overload of your local context.

**Especific envs:**
| env | description | sample |
| ----| ------ | ------ |
|PROJECT| The folder/module name of your project | File |
|FUNCTION| The function module name inside your project | FileProcessingAiMapping |

### How to run
```json
{
  "configurations": [
    {
      "name": "Start File.FileProcessingAiMapping",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/LocalRunner/main.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PORT": "3001",
        "PROJECT": "File",
        "FUNCTION": "FileProcessingAiMapping",
        "ENV_PATH": ".env",
        "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
        "USE_LOCAL_EVENT_EMITTER": "true",
        "KT_DEV_EXEC_MAPPING_CODE_TOPIC_ENDPOINT": "http://localhost:3002/event",
      }
    },
    {
      "name": "Start Utils.CodeExecEvent",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/LocalRunner/main.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
          "PYTHONPATH": "${workspaceFolder}",
          "PORT": "3002",
          "PROJECT": "Utils",
          "FUNCTION": "CodeExecEvent",
          "ENV_PATH": ".env",
          "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
          "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true",
          "USE_LOCAL_EVENT_EMITTER": "true",
      }
    }
  ],
  "compounds": [
    {
      "name": "Start Utils + File",
      "configurations": ["Start Utils.CodeExecEvent", "Start File.FileProcessingAiMapping"]
    }
  ]
}
```

## Usage

The URL format to access your application will be printed in the logs after starting in your terminal.  
You can also access your application documentation at `http://localhost:PORT/docs`.  
Additionally, you can execute requests directly from there.


### HTTP-triggered Functions

**Note**: If your function has a router prefix, you must include it in the request URL.
```json
"route": "prefix/{param1}/{param2?}/{param3?}"
```
so
```sh
POST "http://localhost:3000/api/SampleProject.GetFunction/prefix/param1/param2/param3"
```

### EventGrid-triggered Functions

#### Header Descriptions

- **sync**: If this header is set to `true`, the function will run in sync.\
If not the default behaviour will be in background to simulate the some behavior as a event without locking the the execution of the code.
- **timeout**: This header specifies the maximum time (in seconds) the function should run before timing out. It is useful for simulating scenarios where the code might die before finishing the execution.
- **body request** - To trigger any event, you must always send an array of event JSONs. This is the standard behavior for Event Grid topics.
- **actions** - Events just support `POST` requests.

Example Request
```sh
curl -X POST "http://localhost:3000/event/SampleProject.EventFunction" \
     -H "Content-Type: application/json" \
     -H "async: true" \
     -H "timeout: 300" \
     -d '[
            {
              "id": "1234-5678-91011",
              "data": {
                "exampleField": "exampleValue"
              },
              "topic": "/subscriptions/{subscription-id}/resourceGroups/{resource-group}",
              "subject": "example/subject",
              "eventType": "ExampleEventType",
              "eventTime": "2025-03-16T12:34:56.789Z",
              "dataVersion": "1.0"
            }
        ]'
```
