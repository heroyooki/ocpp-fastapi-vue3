import aio_pika
from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection, AbstractExchange
from loguru import logger

from core.settings import (
    TASKS_EXCHANGE_NAME,
    EVENTS_EXCHANGE_NAME,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    RABBITMQ_PORT,
    RABBITMQ_HOST
)

_connection: AbstractRobustConnection | None = None
_tasks_channel: AbstractRobustChannel | None = None
_events_channel: AbstractRobustChannel | None = None
_exchanges = {}

async def get_connection(
        user=RABBITMQ_USER,
        password=RABBITMQ_PASS,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT
) -> AbstractRobustConnection:
    global _connection
    if not _connection:
        _connection = await connect_robust(
            (
                f"amqp://"
                f"{user}:"
                f"{password}@"
                f"{host}:"
                f"{port}/"
            ),
            timeout=20
        )
        logger.info(
            (
                f"Got queue connection "
                f"(user={user}, "
                f"host={host}, "
                f"port={port})"
            )
        )

    return _connection


async def get_channel(
        connection: AbstractRobustConnection,
        exchange_name: str
) -> AbstractRobustChannel:
    if exchange_name == TASKS_EXCHANGE_NAME:
        global _tasks_channel
        if not _tasks_channel:
            _tasks_channel = await connection.channel()
        return _tasks_channel
    if exchange_name == EVENTS_EXCHANGE_NAME:
        global _events_channel
        if not _events_channel:
            _events_channel = await connection.channel()
        return _events_channel


async def get_exchange(
        channel: AbstractRobustChannel,
        exchange_name: str
) -> AbstractExchange:
    global _exchanges

    if not _exchanges.get(exchange_name):
        _exchanges[exchange_name] = await channel.declare_exchange(
            name=exchange_name,
            type=aio_pika.abc.ExchangeType.FANOUT
        )
    return _exchanges[exchange_name]