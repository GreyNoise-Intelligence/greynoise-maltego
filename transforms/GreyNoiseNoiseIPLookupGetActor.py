from greynoise import GreyNoise
from maltego_trx.entities import ASNumber, Person, Location
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg

from maltego_trx.transform import DiscoverableTransform


class GreyNoiseNoiseIPLookupGetActor(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        api_client = GreyNoise(
            api_key=api_key,
            integration_name="maltego-integration-v2.0.0",
        )

        # make a precise copy of the input to avoid creating a new graph entity
        type_name = "maltego.IPv4Address"
        extra_props = {}
        if request.Genealogy:
            type_name = request.Genealogy[0]["Name"]
            extra_props = request.Properties
        input_ip = response.addEntity(type_name, request.Value)
        for k, v in extra_props.items():
            input_ip.addProperty(fieldName=k, value=v, matchingRule="loose")

        try:
            resp = api_client.ip(request.Value)
            if resp["seen"]:
                if resp["actor"] and resp["actor"] != "unknown":
                    response.addEntity(Person, resp["actor"])
                else:
                    response.addUIMessage(
                        f"The IP address {request.Value} has no associated Actor.")

            else:
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

        except Exception as e:
            response.addUIMessage(e)
