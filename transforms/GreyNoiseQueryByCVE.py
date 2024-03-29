import datetime
import re

from greynoise import GreyNoise
from maltego_trx.maltego import MaltegoMsg
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


class GreyNoiseQueryByCVE(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        query_range = request.TransformSettings["queryTimeRange"]
        asn = request.TransformSettings["asn"]
        actor = request.TransformSettings["actor"]
        port = request.TransformSettings["port"]
        try:
            from_time = int(query_range.split("-")[0].split(".")[0])
            to_time = int(query_range.split("-")[1].split(".")[0])

            modified_from_time = datetime.datetime.fromtimestamp(from_time).strftime("%Y-%m-%d")
            modified_to_time = datetime.datetime.fromtimestamp(to_time).strftime("%Y-%m-%d")
        except ValueError:
            modified_from_time = datetime.datetime.now().strftime("%Y-%m-%d")
            modified_to_time = datetime.datetime.now().strftime("%Y-%m-%d")

        api_client = GreyNoise(api_key=api_key, integration_name=INTEGRATION_NAME)

        # make a precise copy of the input to avoid creating a new graph entity
        type_name = "maltego.CVE"
        extra_props = {}
        if request.Genealogy:
            type_name = request.Genealogy[0]["Name"]
            extra_props = request.Properties
        input_ip = response.addEntity(type_name, request.Value)
        for k, v in extra_props.items():
            input_ip.addProperty(fieldName=k, value=v, matchingRule="loose")

        try:
            cve_pattern = "CVE-\d{4}-\d{4,7}"  # noqa: C605
            match = re.match(cve_pattern, request.Value)
            if match:
                query_string = (
                    "cve:" + request.Value + " last_seen:[" + modified_from_time + " TO " + modified_to_time + "]"
                )
                if asn:
                    query_string = query_string + " asn:AS" + asn
                if actor:
                    query_string = query_string + " actor:'" + actor + "'"
                if port and port != "0":
                    query_string = query_string + " raw_data.scan.port:" + port
                resp = api_client.query(query_string)
                if resp["count"] > 1:
                    for ip_details in resp["data"]:
                        response.addEntity("maltego.IPv4Address", ip_details["ip"])

                else:
                    response.addUIMessage(f"The Query {query_string} did not return any results.")
            else:
                response.addUIMessage(f"{request.Value} is not a properly formatted CVE.")

        except Exception as e:
            response.addUIMessage(e)
