from ocpp.v201.enums import RegistrationStatusType
from pyocpp_contrib.v16.views.events import BootNotificationEvent
from pyocpp_contrib.v16.views.tasks import BootNotificationResponse

from core.utils import get_utc_as_string


async def process_boot_notification(
        session,
        event: BootNotificationEvent
) -> BootNotificationResponse:

    return BootNotificationResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        current_time=get_utc_as_string(),
        interval=20,
        status=RegistrationStatusType.accepted
    )
