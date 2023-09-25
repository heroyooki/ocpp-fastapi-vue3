from copy import deepcopy
from functools import wraps
from typing import Callable, Union

from loguru import logger

from ocpp.v16.enums import Action, ChargePointStatus
from pyocpp_contrib.queue.publisher import publish
from pyocpp_contrib.enums import ConnectionAction
from pyocpp_contrib.v16.views.events import (
    SecurityEventNotificationEvent,
    StatusNotificationEvent,
    BootNotificationEvent,
    HeartbeatEvent,
    LostConnectionEvent,
    AuthorizeEvent,
    StartTransactionEvent,
    StopTransactionEvent,
    MeterValuesEvent
)

from core.database import get_contextual_session
from manager.services.ocpp.boot_notification import process_boot_notification
from manager.services.charge_points import update_charge_point
from manager.services.ocpp.heartbeat import process_heartbeat
from manager.services.ocpp.meter_values import process_meter_values
from manager.services.ocpp.security_event_notification import process_security_event_notification
from manager.services.ocpp.start_transaction import process_start_transaction
from manager.services.ocpp.status_notification import process_status_notification
from manager.services.ocpp.authorize import process_authorize
from manager.services.ocpp.stop_transaction import process_stop_transaction
from manager.views.charge_points import ChargePointUpdateStatusView
from sse import sse_publisher


def prepare_event(func) -> Callable:
    @wraps(func)
    async def wrapper(data):
        logger.info(f"Got event from charge point node (event={data})")

        event = {
            ConnectionAction.lost_connection: LostConnectionEvent,
            Action.StatusNotification: StatusNotificationEvent,
            Action.BootNotification: BootNotificationEvent,
            Action.Heartbeat: HeartbeatEvent,
            Action.SecurityEventNotification: SecurityEventNotificationEvent,
            Action.Authorize: AuthorizeEvent,
            Action.StartTransaction: StartTransactionEvent,
            Action.StopTransaction: StopTransactionEvent,
            Action.MeterValues: MeterValuesEvent
        }[data["action"]](**data)
        return await func(event)

    return wrapper


@prepare_event
@sse_publisher.publish
async def process_event(event: Union[
    LostConnectionEvent,
    StatusNotificationEvent,
    BootNotificationEvent,
    HeartbeatEvent,
    SecurityEventNotificationEvent,
    AuthorizeEvent,
    StartTransactionEvent,
    StopTransactionEvent,
    MeterValuesEvent
]) -> Union[
    LostConnectionEvent,
    StatusNotificationEvent,
    BootNotificationEvent,
    HeartbeatEvent,
    SecurityEventNotificationEvent,
    AuthorizeEvent,
    StartTransactionEvent,
    StopTransactionEvent,
    MeterValuesEvent
] | None:
    task = None

    async with get_contextual_session() as session:

        if event.action is Action.MeterValues:
            task = await process_meter_values(session, deepcopy(event))
        if event.action is Action.StopTransaction:
            task = await process_stop_transaction(session, deepcopy(event))
            event.transaction_id = event.payload.transaction_id
        if event.action is Action.StartTransaction:
            task = await process_start_transaction(session, deepcopy(event))
            event.transaction_id = task.transaction_id
        if event.action is Action.Authorize:
            task = await process_authorize(session, deepcopy(event))
        if event.action is Action.SecurityEventNotification:
            task = await process_security_event_notification(session, deepcopy(event))
        if event.action is Action.BootNotification:
            task = await process_boot_notification(session, deepcopy(event))
        if event.action is Action.StatusNotification:
            task = await process_status_notification(session, deepcopy(event))
        if event.action is Action.Heartbeat:
            task = await process_heartbeat(session, deepcopy(event))

        if event.action is ConnectionAction.lost_connection:
            data = ChargePointUpdateStatusView(status=ChargePointStatus.unavailable)
            await update_charge_point(session, charge_point_id=event.charge_point_id, data=data)

        if task:
            await publish(task.json(), to=task.exchange, priority=task.priority)

        await session.commit()
        await session.close()
        logger.info(f"Successfully completed process event={event}")

        return event
