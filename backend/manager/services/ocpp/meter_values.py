from pyocpp_contrib.v16.views.events import MeterValuesEvent
from pyocpp_contrib.v16.views.tasks import MeterValuesResponse


async def process_meter_values(
        session,
        event: MeterValuesEvent
) -> MeterValuesResponse:

    payload = event.payload

    return MeterValuesResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
