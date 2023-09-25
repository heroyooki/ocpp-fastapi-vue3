from typing import Tuple

from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger
from pyocpp_contrib.queue.publisher import publish

from core.database import get_contextual_session
from manager.models import AuthData, Account, ChargePoint
from manager.services.accounts import get_account
from manager.services.charge_points import (
    get_charge_point,
    get_statuses_counts, create_charge_point, build_charge_points_query, remove_charge_point
)
from manager.utils import acquire_lock, params_extractor, paginate
from manager.views.charge_points import StatusCount, PaginatedChargePointsView, CreateChargPointView

charge_points_router = APIRouter(
    tags=["charge_points"]
)


@charge_points_router.post(
    "/charge_points/{charge_point_id}",
    status_code=status.HTTP_200_OK
)
async def authenticate(charge_point_id: str, data: AuthData | None = None):
    logger.info(f"Start authenticate charge point (id={charge_point_id})")
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        if not charge_point:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        await session.close()


@charge_points_router.get(
    "/{account_id}/charge_points",
    status_code=status.HTTP_200_OK
)
async def list_charge_points(
        search: str = "",
        account: Account = Depends(get_account),
        params: Tuple = Depends(params_extractor)
) -> PaginatedChargePointsView:
    async with get_contextual_session() as session:
        items, pagination = await paginate(
            session,
            lambda: build_charge_points_query(account, search),
            *params
        )
        await session.close()
        return PaginatedChargePointsView(items=[item[0] for item in items], pagination=pagination)


@charge_points_router.post(
    "/{account_id}/charge_points",
    status_code=status.HTTP_201_CREATED,
)
async def add_charge_point(
        data: CreateChargPointView,
        account: Account = Depends(get_account)
):
    async with get_contextual_session() as session:
        await create_charge_point(session, data)
        await session.commit()
        await session.close()


@charge_points_router.get(
    "/{account_id}/charge_points/counters",
    status_code=status.HTTP_200_OK,
    response_model=StatusCount
)
async def get_counters(account: Account = Depends(get_account)):
    async with get_contextual_session() as session:
        counters = await get_statuses_counts(session, account.id)
        await session.close()
        return counters


@charge_points_router.delete(
    "/{account_id}/charge_points/{charge_point_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_charge_point(
        charge_point_id: str,
        account: Account = Depends(get_account),
):
        async with get_contextual_session() as session:
            await remove_charge_point(session, charge_point_id)
            await session.commit()
            await session.close()
