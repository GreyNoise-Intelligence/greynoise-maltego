from greynoise import GreyNoise
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg

from maltego_trx.transform import DiscoverableTransform


def add_display_info(ip_ent: MaltegoEntity, classification, last_seen, link, name, tags):
    link_text = ""
    if link:
        link_text = f'<h3><a href="{link}">Open in GreyNoise</a></h3> <br/>'

    classification_text = ""
    if classification:
        classification_text = f"GreyNoise classification for IP: {classification}<br/>"

    name_text = ""
    if name and name != "unknown":
        name_text = f"GreyNoise attribution: {name}<br/>"

    last_seen_text = "" if not last_seen else f"Last seen by GreyNoise: {last_seen}"

    tag_text = ""
    if tags:
        tags_list=",".join(tags)
        tag_text = f"GreyNoise Tags: {tags_list}"


    ip_ent.addDisplayInformation(
        f"{link_text}{classification_text}{name_text}{last_seen_text}{tag_text}",
        "GreyNoise",
    )
    colour = None
    if classification == "benign":
        colour = "#45e06f"
    elif classification == "malicious":
        colour = "#eb4d4b"

    if colour:
        ip_ent.addProperty(
            fieldName="gn_color",
            displayName="GreyNoise color",
            value=colour,
            matchingRule="loose",
        )
        ip_ent.addOverlay(
            propertyName="gn_color",
            position=OverlayPosition.NORTH_WEST,
            overlayType=OverlayType.COLOUR,
        )


class GreyNoiseNoiseIPLookup(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):
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
                response.addEntity("greynoise.noise", "Noise Detected")

                if resp["actor"] != "unknown":
                    response.addEntity("maltego.Organization", resp["actor"])

                response.addEntity("greynoise.classification", resp["classification"])

                if resp["vpn"]:
                    respon.addEntity("maltego.Service", "VPN Service: " + resp.get("vpn_service"))

                if resp["bot"]:
                    respon.addEntity("maltego.Service", "Common Bot Activity")

                if resp["metadata"]["tor"]:
                    respon.addEntity("maltego.Service", "Tor Exit Node")

                for cve in resp["cve"]:
                    respon.addEntity("maltego.CVE", cve)

                resp["link"] = "https://www.greynoise.io/viz/ip/" + resp["ip"]
                # add dynamic properties instead of returning more to the graph
                input_ip.addProperty(
                    fieldName="gn_url",
                    displayName="GreyNoise URL",
                    value=resp["link"],
                    matchingRule="loose",
                )
                input_ip.addProperty(
                    fieldName="gn_last_seen",
                    displayName="GreyNoise last seen",
                    value=resp["last_seen"],
                    matchingRule="loose",
                )
            else:
                response.addEntity("greynoise.noise", "No Noise Detected")
                response.addUIMessage(
                    f"The IP address {request.Value} hasn't been seen by GreyNoise."
                )

            add_display_info(
                input_ip,
                resp.get("classification"),
                resp.get("last_seen"),
                resp.get("link"),
                resp.get("actor"),
                resp.get("tags")
            )
        except Exception as e:
            response.addUIMessage(e)
