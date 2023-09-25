from ocpp.v16.enums import AuthorizationStatus
from pyocpp_contrib.v16.views.events import StopTransactionEvent
from pyocpp_contrib.v16.views.tasks import StopTransactionResponse

from manager.services.transactions import update_transaction
from manager.views.transactions import UpdateTransactionView


async def process_stop_transaction(
        session,
        event: StopTransactionEvent
) -> StopTransactionResponse:

    view = UpdateTransactionView(
        transaction_id=event.payload.transaction_id,
        meter_stop=event.payload.meter_stop
    )
    await update_transaction(session, event.payload.transaction_id, view)

    return StopTransactionResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        id_tag_info={"status": AuthorizationStatus.accepted.value}
    )
