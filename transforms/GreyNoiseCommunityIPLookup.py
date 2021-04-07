from greynoise import GreyNoise
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.maltego import MaltegoEntity
from maltego_trx.transform import DiscoverableTransform


def add_display_info(ip_ent: MaltegoEntity, classification, last_seen, link):
    link_text = "" if not link else f'<h3><a href="{link}">Open in GreyNoise</a></h3> <br/>'
    classification_text = "" if not classification else f"GreyNoise classification for IP: {classification}<br/>"
    last_seen_text = "" if not last_seen else f"Last seen by GreyNoise: {last_seen}"
    ip_ent.addDisplayInformation(
        f"{link_text}{classification_text}{last_seen_text}",
        "GreyNoise Community"
    )
    colour = None
    if classification == "benign":
        colour = "#45e06f"
    elif classification == "malicious":
        colour = "#eb4d4b"

    if colour:
        ip_ent.addProperty(fieldName="gn_color", displayName="GreyNoise color", value=colour, matchingRule="loose")
        ip_ent.addOverlay(propertyName="gn_color", position=OverlayPosition.NORTH_WEST, overlayType=OverlayType.COLOUR)


class GreyNoiseCommunityIPLookup(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        api_key = request.TransformSettings["GNApiKey"]
        api_client = GreyNoise(
            api_key=api_key,
            integration_name="maltego-community-v1.0.0",
            offering="community",
        )
        input_ip = response.addEntity("maltego.IPv4Address", request.Value)
        try:
            resp = api_client.ip(request.Value)
            if resp["noise"] or resp["riot"]:
                if resp["noise"]:
                    response.addEntity("greynoise.noise", "Noise Detected")
                if resp["riot"]:
                    response.addEntity("greynoise.noise", "Benign Service Detected")
                response.addEntity("maltego.Alias", resp["name"])
                response.addEntity("greynoise.classification", resp["classification"])
                response.addEntity("maltego.DateTime", resp["last_seen"])
                url = response.addEntity("maltego.URL", resp["link"])
                url.addProperty(
                    fieldName="short-title", displayName="GreyNoise color", value=resp["link"], matchingRule="strict"
                )
                url.addProperty(
                    fieldName="url", displayName="GreyNoise color", value=resp["link"], matchingRule="strict"
                )
            else:
                response.addEntity("greynoise.noise", "No Noise Detected")
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

            add_display_info(input_ip, resp.get("classification"), resp.get("last_seen"), resp.get("link"))
        except Exception as e:
            response.addUIMessage(e)
