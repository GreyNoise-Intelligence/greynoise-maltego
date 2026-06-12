from greynoise.api import APIConfig, GreyNoise
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


def add_display_info(ip_ent: MaltegoEntity, classification, last_updated, link, name):
    link_text = ""
    if link:
        link_text = f'<h3><a href="{link}">Open in GreyNoise</a></h3> <br/>'

    classification_text = ""
    if classification:
        classification_text = f"GreyNoise classification for IP: {classification}<br/>"

    name_text = ""
    if name and name != "unknown":
        name_text = f"GreyNoise attribution: {name}<br/>"

    last_updated_text = "" if not last_updated else f"Last updated by GreyNoise: {last_updated}"

    ip_ent.addDisplayInformation(
        f"{link_text}{classification_text}{name_text}{last_updated_text}",
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


class GreyNoiseRIOTIPLookup(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):
        api_key = request.TransformSettings["GNApiKey"]
        api_config = APIConfig(api_key=api_key, integration_name=INTEGRATION_NAME)
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
            if lookup_response.get("business_service_intelligence", {}).get("found", False):
                classification = ""
                response.addEntity("greynoise.noise", "Common Business Service Detected")

                if lookup_response.get("business_service_intelligence", {}).get("name", "unknown") != "unknown":
                    response.addEntity(
                        "maltego.Organization",
                        lookup_response.get("business_service_intelligence", {}).get("name", "unknown"),
                    )

                if lookup_response.get("business_service_intelligence", {}).get("trust_level", "unknown") == "1":
                    classification = "BSI - Reasonably Ignore"
                    response.addEntity("greynoise.classification", classification)
                elif lookup_response.get("business_service_intelligence", {}).get("trust_level", "unknown") == "2":
                    classification = "BSI - Commonly Seen"
                    response.addEntity("greynoise.classification", classification)
                elif lookup_response.get("business_service_intelligence", {}).get("trust_level", "unknown") == "3":
                    classification = "BSI - Context Only"
                    response.addEntity("greynoise.classification", classification)
                else:
                    classification = "BSI - Unknown"
                    response.addEntity("greynoise.classification", classification)

                lookup_response["link"] = "https://www.greynoise.io/viz/ip/" + request.Value

                # add dynamic properties instead of returning more to the graph
                input_ip.addProperty(
                    fieldName="gn_url",
                    displayName="GreyNoise URL",
                    value=lookup_response["link"],
                    matchingRule="loose",
                )
                input_ip.addProperty(
                    fieldName="gn_last_updated",
                    displayName="GreyNoise last updated",
                    value=lookup_response.get("business_service_intelligence", {}).get("last_updated", "unknown"),
                    matchingRule="loose",
                )
            else:
                response.addEntity("greynoise.noise", "Not a Common Business Service")
                response.addUIMessage(f"The IP address {request.Value} is not found in GreyNoise RIOT IP Dataset.")

            add_display_info(
                input_ip,
                classification,
                lookup_response.get("business_service_intelligence", {}).get("last_updated", None),
                lookup_response.get("link"),
                lookup_response.get("business_service_intelligence", {}).get("name", "unknown"),
            )
        except Exception as e:
            response.addUIMessage(e)
