import asyncio

from loguru import logger

from core.queue.consumer import start_consume
from core.settings import EVENTS_QUEUE_NAME
from manager import app
from manager.controllers.accounts import accounts_router
from manager.controllers.charge_points import charge_points_router
from manager.controllers.common import common_router
from manager.controllers.locations import locations_router
from manager.services.accounts import list_accounts
from manager.services.events import process_event
from sse.controllers import stream_router

background_tasks = set()


@app.on_event("startup")
async def startup():
    # Save a reference to the result of this function, to avoid a task disappearing mid-execution.
    # The event loop only keeps weak references to tasks.
    task = asyncio.create_task(
        start_consume(queue_name=EVENTS_QUEUE_NAME, on_message=process_event)
    )
    background_tasks.add(task)

    accounts = await list_accounts()
    logger.info(f"Started up application with accounts = ({accounts}).")


app.include_router(common_router)
app.include_router(stream_router)
app.include_router(charge_points_router)
app.include_router(locations_router)
app.include_router(accounts_router)
