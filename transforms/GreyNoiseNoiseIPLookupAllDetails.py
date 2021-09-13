from greynoise import GreyNoise
from maltego_trx.entities import ASNumber, Person, Location
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

    last_seen_text = "" if not last_seen else f"Last seen by GreyNoise: {last_seen}<br/>"

    tag_text = ""
    if tags:
        tags_list = ", ".join(tags)
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


class GreyNoiseNoiseIPLookupAllDetails(DiscoverableTransform):
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
                response.addEntity("greynoise.noise", "Noise Detected")

                if resp["actor"] != "unknown":
                    response.addEntity(Person, resp["actor"])

                if resp["classification"]:
                    response.addEntity("greynoise.classification", resp["classification"])

                if resp["metadata"]["asn"]:
                    response.addEntity(ASNumber, str(resp["metadata"]["asn"]).replace("AS", ""))

                if resp["metadata"]["organization"]:
                    response.addEntity("maltego.Company", resp["metadata"]["organization"])

                if resp["metadata"]["city"] and resp["metadata"]["country"] and resp["metadata"]["country_code"]:
                    response.addEntity(
                        Location, "{0}, {1} ({2})".format(resp["metadata"]["city"], resp["metadata"]["country"], resp["metadata"]["country_code"])
                    )

                if resp["vpn"]:
                    response.addEntity("maltego.Service", "VPN Service: " + resp.get("vpn_service"))

                if resp["bot"]:
                    response.addEntity("maltego.Service", "Common Bot Activity")

                if resp["metadata"]["tor"]:
                    response.addEntity("maltego.Service", "Tor Exit Node")

                for cve in resp["cve"]:
                    cve_entity = response.addEntity("maltego.CVE", cve)
                    cve_entity.setLinkLabel("Probes For")

                for item in resp["raw_data"]["scan"]:
                    port_entity = response.addEntity("maltego.Port", item["port"])
                    port_entity.setLinkLabel("Scans For")

                for tag in resp["tags"]:
                    response.addEntity("maltego.Phrase", tag)

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
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

            add_display_info(
                input_ip,
                resp.get("classification"),
                resp.get("last_seen"),
                resp.get("link"),
                resp.get("actor"),
                resp.get("tags"),
            )
        except Exception as e:
            response.addUIMessage(e)
