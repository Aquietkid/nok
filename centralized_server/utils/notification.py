from pydantic import BaseModel
from firebase_admin import messaging


class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str


def send_notification(data: NotificationRequest):
    message = messaging.Message(
        token=data.token,
        notification=messaging.Notification(
            title=data.title,
            body=data.body
        )
    )
    result = messaging.send(message)
    print(result)
    return result
