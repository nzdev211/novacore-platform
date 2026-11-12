from novacore.kernel.identity import RequestId
from novacore.kernel.request import Request

request = Request(
    id=RequestId("request-001"),
    description=(
        "Create a cinematic marketing campaign "
        "for a new product launch."
    ),
)
