from azure.functions import EventGridEvent

class EventRequest(EventGridEvent):
    def __init__(self, body: dict):
        super().__init__(
            id=body.get("id"),
            data=body.get("data"),
            topic=body.get("topic"),
            subject=body.get("subject"),
            event_type=body.get("eventType"),
            event_time=body.get("eventTime"),
            data_version=body.get("dataVersion")
        )