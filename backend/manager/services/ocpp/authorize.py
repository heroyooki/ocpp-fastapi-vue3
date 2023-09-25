from ocpp.v16.enums import AuthorizationStatus
from pyocpp_contrib.v16.views.events import AuthorizeEvent
from pyocpp_contrib.v16.views.tasks import AuthorizeResponse


async def process_authorize(session, event: AuthorizeEvent) -> AuthorizeResponse:

    return AuthorizeResponse(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        id_tag_info={"status": AuthorizationStatus.accepted.value}
    )
