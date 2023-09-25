from __future__ import annotations

from functools import wraps
from typing import List, Callable, Union

from loguru import logger
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

import manager.services.charge_points as service
from core import settings
from core.database import get_contextual_session
from sse import observer as obs
from sse.views import Redactor


class Publisher:
    observers: List[obs.Observer] = []

    def __init__(self, redactor: Redactor):
        self.redactor = redactor

    async def notify_observer(
            self,
            observer: obs.Observer,
            event: Union[
                LostConnectionEvent,
                StatusNotificationEvent,
                BootNotificationEvent,
                HeartbeatEvent,
                SecurityEventNotificationEvent,
                AuthorizeEvent,
                StartTransactionEvent,
                StopTransactionEvent,
                MeterValuesEvent]
    ) -> None:
        event = await self.redactor.prepare_event(event, observer.account.id)
        if event:
            await observer.gain_event(event)

    async def ensure_observers(self) -> None:
        """
        Remove inactive observers from the 'observers' list.
        :return:
        """
        for observer in self.observers:
            if await observer.request.is_disconnected():
                self.observers.remove(observer)
                del observer

    def publish(self, func) -> Callable:
        """
        Publish new event for all observers in the list
        :param func:
        :return:
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = await func(*args, **kwargs)
            if event and event.action in settings.ALLOWED_SERVER_SENT_EVENTS:
                logger.info(f"Start sending sse (event={event})")
                async with get_contextual_session() as session:
                    charge_point = await service.get_charge_point(
                        session,
                        event.charge_point_id
                    )
                    if charge_point:
                        for observer in self.observers:
                            if charge_point.location.account.id == observer.account.id:
                                await self.notify_observer(observer, event)

        return wrapper

    async def add_observer(self, observer: obs.Observer) -> None:
        await self.ensure_observers()
        self.observers.append(observer)

    async def remove_observer(self, observer: obs.Observer) -> None:
        self.observers.remove(observer)
