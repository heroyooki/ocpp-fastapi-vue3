from ocpp.v16.enums import ChargePointStatus
from pyocpp_contrib.v16.views.events import HeartbeatEvent
from pyocpp_contrib.v16.views.tasks import HeartbeatResponse

from core.utils import get_utc_as_string
from manager.services.charge_points import update_charge_point
from manager.views.charge_points import ChargePointUpdateStatusView


async def process_heartbeat(session, event: HeartbeatEvent) -> HeartbeatResponse:
    # Do some logic here
    data = ChargePointUpdateStatusView(status=ChargePointStatus.available)
    await update_charge_point(session, event.charge_point_id, data=data)
    return HeartbeatResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        current_time=get_utc_as_string()
    )
