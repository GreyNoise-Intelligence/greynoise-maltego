import utility

from greynoise import GreyNoise
from maltego_trx.entities import ASNumber, Person, Location
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.transform import DiscoverableTransform


class GreyNoiseNoiseIPSims(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        api_client = GreyNoise(
            api_key=api_key,
            integration_name=INTEGRATION_NAME
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
            resp = api_client.similar(request.Value)
            if resp["similar_ips"]:
                for item in resp["similar_ips"]:
                    response.addEntity("maltego.IPv4Address", item["ip"])

            else:
                response.addUIMessage(
                    f"The IP address {request.Value} has no similar IPs within GreyNoise.")

        except Exception as e:
            response.addUIMessage(e)
