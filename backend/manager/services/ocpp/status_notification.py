from ocpp.v16.enums import ChargePointStatus
from sqlalchemy.ext.asyncio import AsyncSession
from pyocpp_contrib.v16.views.events import StatusNotificationEvent
from pyocpp_contrib.v16.views.tasks import StatusNotificationResponse

from manager.services.charge_points import update_connectors, update_charge_point
from manager.views.charge_points import ChargePointUpdateStatusView


async def process_status_notification(
        session: AsyncSession,
        event: StatusNotificationEvent
) -> StatusNotificationResponse:

    await update_connectors(session, event)

    if event.payload.connector_id == 0:
        data = ChargePointUpdateStatusView(status=ChargePointStatus.available)
        await update_charge_point(session, event.charge_point_id, data=data)

    return StatusNotificationResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
