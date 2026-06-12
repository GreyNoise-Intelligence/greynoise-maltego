import datetime

from greynoise.api import APIConfig, GreyNoise
from maltego_trx.maltego import MaltegoMsg
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


class GreyNoiseQueryByASN(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        query_range = request.TransformSettings["queryTimeRange"]
        try:
            from_time = int(query_range.split("-")[0].split(".")[0])
            from_date = datetime.datetime.fromtimestamp(from_time).date()
            today = datetime.datetime.now().date()
            days_from_today = (today - from_date).days
            last_seen = f"{min(max(days_from_today, 1), 90)}d"
        except ValueError:
            last_seen = "1d"
        api_config = APIConfig(api_key=api_key, integration_name=INTEGRATION_NAME)
        api_client = GreyNoise(api_config)

        # make a precise copy of the input to avoid creating a new graph entity
        type_name = "maltego.AS"
        extra_props = {}
        if request.Genealogy:
            type_name = request.Genealogy[0]["Name"]
            extra_props = request.Properties
        input_ip = response.addEntity(type_name, request.Value)
        for k, v in extra_props.items():
            input_ip.addProperty(fieldName=k, value=v, matchingRule="loose")

        try:
            query_string = "metadata.asn:AS" + request.Value + " last_seen:" + last_seen
            query_response = api_client.query(query_string, quick=True)
            if query_response.get("request_metadata", {}).get("count", 0) > 1:
                for ip_details in query_response.get("data", []):
                    response.addEntity("maltego.IPv4Address", ip_details["ip"])

            else:
                response.addUIMessage(f"The Query {query_string} did not return any results.")

        except Exception as e:
            response.addUIMessage(e)
