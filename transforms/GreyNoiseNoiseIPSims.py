from greynoise import GreyNoise
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


def add_display_info(ip_ent: MaltegoEntity, similar_ips, ip_address, minimum_score):
    link_text = (
        f'<h3><a href="https://viz.greynoise.io/ip-similarity/{ip_address}">'
        f"See Similarity results in GreyNoise</a></h3><br/>"
    )

    minimum_score_percentage = str(int(minimum_score) * 100)
    similarity_text = (
        f"IP address {ip_address} is similar to {similar_ips} "
        f"above a {minimum_score_percentage}% in the GreyNoise data set<br/>"
    )

    ip_ent.addDisplayInformation(
        f"{link_text}{similarity_text}",
        "GreyNoise Similarity",
    )


class GreyNoiseNoiseIPSims(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):  # noqa: C901
        api_key = request.TransformSettings["GNApiKey"]
        limit = request.TransformSettings["limit"]
        minimum_score = request.TransformSettings["minimum_score"]
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

        if not limit:
            limit = 50
        elif isinstance(limit, str):
            limit = int(limit)

        if not minimum_score:
            minimum_score = 90
        elif isinstance(minimum_score, str):
            minimum_score = int(minimum_score)

        try:
            resp = api_client.similar(request.Value, min_score=minimum_score, limit=limit)
            if "similar_ips" in resp:
                similar_ips = len(resp["similar_ips"])
                for item in resp["similar_ips"]:
                    response.addEntity("maltego.IPv4Address", item["ip"])

                add_display_info(
                    input_ip,
                    similar_ips,
                    resp["ip"].get("ip"),
                    minimum_score,
                )

            else:
                response.addUIMessage(f"The IP address {request.Value} has no similar IPs within GreyNoise.")

        except Exception as e:
            response.addUIMessage(e)
