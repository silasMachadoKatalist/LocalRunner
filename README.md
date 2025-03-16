# Local Azure Functions Proxy

This project provides a local proxy for Azure Functions, allowing you to test and debug your Azure Functions locally using FastAPI. The proxy supports both HTTP-triggered functions and EventGrid-triggered functions. Additionally, it supports hot reload, enabling you to see changes in real-time without restarting the server. Dependencies are dynamically loaded on the first request, ensuring that the latest versions are always used.

## Why This Project Was Created
This project was created to provide a local development environment for Azure Functions, allowing developers to test and debug their functions locally before deploying them to Azure. The main reason for this project is due to the structure we have, where everything runs from the root of the project, and our pipeline needs to copy the ShareLibraries folder into the function's context. Additionally, we are unable to run Azurite locally due to the way the project is structured. By using FastAPI as a proxy, developers can easily simulate HTTP and EventGrid triggers and ensure their functions behave as expected.

## Setup

1. **Install dependencies**:
```sh
pip install -r requirements.txt
```

## Starting

### If running from vscode
1. Add the follow configuration to your launch.json
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Local Azure Functions Proxy",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/LocalRunner/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "ENV_PATH": ".env",
                "USE_LOCAL_ENV_HANDLER_ENVIRONMENT": "true",
                "USE_LOCAL_KEYVAULT_HANDLER_ENVIRONMENT": "true"
            }
        }
    ]
}
```

## Usage

### HTTP-triggered Functions

To call an HTTP-triggered function, use the following URL format:
```
http://localhost:3000/api/{ProjectName}.{FunctionName}
```
#### **Example Resquest**
```sh
curl -X POST "http://localhost:3000/api/SampleProject.GetFunction" \
     -H "Content-Type: application/json" \
     -d '{
           "param1": "value1",
           "param2": "value2"
         }'
```

**Note**: If your function has a router prefix you must pass it together in the request
```json
"route": "prefix/{param1}/{param2?}/{param3?}"
```
so
```sh
POST "http://localhost:3000/api/SampleProject.GetFunction/prefix/param1/param2/param3"
```

<br>

---

<br>

### EventGrid-triggered Functions
To call an EventGrid-triggered function, use the following URL format:
```
http://localhost:3000/event/{ProjectName}.{FunctionName}
```

Example Request
```sh
curl -X POST "http://localhost:3000/event/SampleProject.EventFunction" \
     -H "Content-Type: application/json" \
     -H "async: true" \
     -H "timeout: 300" \
     -d '{
           "id": "1234-5678-91011",
           "data": {
             "exampleField": "exampleValue"
           },
           "topic": "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.EventGrid/topics/{topic-name}",
           "subject": "example/subject",
           "eventType": "ExampleEventType",
           "eventTime": "2025-03-16T12:34:56.789Z",
           "dataVersion": "1.0"
         }'
```

#### Header Descriptions

- **async**: If this header is set to `true`, the function will run in the background. This is useful for testing integration across events locally without blocking the main thread.
- **timeout**: This header specifies the maximum time (in seconds) the function should run before timing out. It is useful for simulating scenarios where the code might die before finishing the execution.
