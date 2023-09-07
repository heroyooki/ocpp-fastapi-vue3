from ocpp.v16.enums import Action

from charge_point_node.models.base import BaseEvent


class SecurityEventNotificationEvent(BaseEvent):
    action: Action = Action.SecurityEventNotification
