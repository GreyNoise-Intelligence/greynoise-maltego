from greynoise import GreyNoise
from maltego_trx.entities import ASNumber, Person, Location
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg

from maltego_trx.transform import DiscoverableTransform


class GreyNoiseQueryByActor(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        query_range = request.TransformSettings["queryTimeRange"]
        api_client = GreyNoise(
            api_key=api_key,
            integration_name="maltego-integration-v2.0.0",
        )

        # make a precise copy of the input to avoid creating a new graph entity
        type_name = "maltego.Person"
        extra_props = {}
        if request.Genealogy:
            type_name = request.Genealogy[0]["Name"]
            extra_props = request.Properties
        input_ip = response.addEntity(type_name, request.Value)
        for k, v in extra_props.items():
            input_ip.addProperty(fieldName=k, value=v, matchingRule="loose")

        try:
            query_string = "actor:" + request.Value + " last_seen:" + query_range
            resp = api_client.query(query_string)
            if resp["count"] > 1:
                for ip_details in resp["data"]:
                    response.addEntity("maltego.IPv4Address", ip_details["ip"])

            else:
                response.addUIMessage(f"The Query {query_string} did not return any results.")

        except Exception as e:
            response.addUIMessage(e)
