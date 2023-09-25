import asyncio

from loguru import logger
from pyocpp_contrib.queue.consumer import start_consume
from pyocpp_contrib.settings import EVENTS_EXCHANGE_NAME

from core.database import get_contextual_session
from manager import app
from manager.controllers.accounts import accounts_router
from manager.controllers.charge_points import charge_points_router
from manager.controllers.common import common_router
from manager.controllers.locations import locations_router
from manager.controllers.transactions import transaction_router
from manager.services.accounts import list_accounts
from manager.events import process_event
from sse.controllers import stream_router

background_tasks = set()


@app.on_event("startup")
async def startup():
    # Save a reference to the result of this function, to avoid a task disappearing mid-execution.
    # The event loop only keeps weak references to tasks.
    task = asyncio.create_task(
        start_consume(exchange_name=EVENTS_EXCHANGE_NAME, on_message=process_event)
    )
    background_tasks.add(task)

    async with get_contextual_session() as session:
        accounts = await list_accounts(session)
        logger.info(f"Started up application with accounts = ({accounts}).")


app.include_router(accounts_router)
app.include_router(common_router)
app.include_router(stream_router)
app.include_router(charge_points_router)
app.include_router(locations_router)
app.include_router(transaction_router)
