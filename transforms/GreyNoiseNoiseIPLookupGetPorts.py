from greynoise.api import APIConfig, GreyNoise
from maltego_trx.maltego import MaltegoMsg
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


class GreyNoiseNoiseIPLookupGetPorts(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        api_config = APIConfig(
            api_key=api_key,
            integration_name=INTEGRATION_NAME,
        )
        api_client = GreyNoise(api_config)

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
            lookup_response = api_client.ip(request.Value)
            if lookup_response.get("internet_scanner_intelligence", {}).get("found", False):
                if lookup_response.get("internet_scanner_intelligence", {}).get("raw_data", {}).get("scan", []):
                    for item in (
                        lookup_response.get("internet_scanner_intelligence", {}).get("raw_data", {}).get("scan", [])
                    ):
                        port_entity = response.addEntity("maltego.Port", item["port"])
                        port_entity.setLinkLabel("Scans For")
                else:
                    response.addUIMessage(f"The IP address {request.Value} has no associated Ports.")

            else:
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

        except Exception as e:
            response.addUIMessage(e)
