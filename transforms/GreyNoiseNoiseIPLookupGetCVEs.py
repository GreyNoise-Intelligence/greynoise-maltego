from greynoise import GreyNoise
from maltego_trx.maltego import MaltegoMsg
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


class GreyNoiseNoiseIPLookupGetCVEs(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        api_client = GreyNoise(api_key=api_key, integration_name=INTEGRATION_NAME)

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
                if resp["cve"]:
                    for cve in resp["cve"]:
                        cve_entity = response.addEntity("maltego.CVE", cve)
                        cve_entity.setLinkLabel("Probes For")
                else:
                    response.addUIMessage(f"The IP address {request.Value} has no associated CVEs.")

            else:
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

        except Exception as e:
            response.addUIMessage(e)
