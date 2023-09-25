from pyocpp_contrib.v16.views.events import SecurityEventNotificationEvent
from pyocpp_contrib.v16.views.tasks import SecurityEventNotificationResponse


async def process_security_event_notification(
        session,
        event: SecurityEventNotificationEvent
) -> SecurityEventNotificationResponse:
    # Do some logic here

    return SecurityEventNotificationResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
