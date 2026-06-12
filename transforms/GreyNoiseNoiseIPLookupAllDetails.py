from greynoise.api import APIConfig, GreyNoise
from maltego_trx.entities import ASNumber, Location, Person
from maltego_trx.maltego import MaltegoEntity, MaltegoMsg
from maltego_trx.overlays import OverlayPosition, OverlayType
from maltego_trx.transform import DiscoverableTransform

from .utility import INTEGRATION_NAME


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
    elif classification == "suspicious":
        colour = "#ffa500"

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
                response.addEntity("greynoise.noise", "Noise Detected")

                if lookup_response.get("internet_scanner_intelligence", {}).get("actor", "unknown") != "unknown":
                    response.addEntity(
                        Person, lookup_response.get("internet_scanner_intelligence", {}).get("actor", "unknown")
                    )

                if lookup_response.get("internet_scanner_intelligence", {}).get("classification"):
                    response.addEntity(
                        "greynoise.classification",
                        lookup_response.get("internet_scanner_intelligence", {}).get("classification"),
                    )

                if lookup_response.get("internet_scanner_intelligence", {}).get("metadata", {}).get("asn"):
                    response.addEntity(
                        ASNumber,
                        str(
                            lookup_response.get("internet_scanner_intelligence", {}).get("metadata", {}).get("asn")
                        ).replace("AS", ""),
                    )

                if lookup_response.get("internet_scanner_intelligence", {}).get("metadata", {}).get("organization"):
                    response.addEntity(
                        "maltego.Company",
                        lookup_response.get("internet_scanner_intelligence", {})
                        .get("metadata", {})
                        .get("organization"),
                    )

                if (
                    lookup_response.get("internet_scanner_intelligence", {}).get("metadata", {}).get("source_city")
                    and lookup_response.get("internet_scanner_intelligence", {})
                    .get("metadata", {})
                    .get("source_country")
                    and lookup_response.get("internet_scanner_intelligence", {})
                    .get("metadata", {})
                    .get("source_country_code")
                ):
                    response.addEntity(
                        Location,
                        "{0}, {1} ({2})".format(
                            lookup_response.get("internet_scanner_intelligence", {})
                            .get("metadata", {})
                            .get("source_city"),
                            lookup_response.get("internet_scanner_intelligence", {})
                            .get("metadata", {})
                            .get("source_country"),
                            lookup_response.get("internet_scanner_intelligence", {})
                            .get("metadata", {})
                            .get("source_country_code"),
                        ),
                    )

                if lookup_response.get("internet_scanner_intelligence", {}).get("vpn"):
                    response.addEntity(
                        "maltego.Service",
                        "VPN Service: " + lookup_response.get("internet_scanner_intelligence", {}).get("vpn_service"),
                    )

                if lookup_response.get("internet_scanner_intelligence", {}).get("metadata", {}).get("tor"):
                    response.addEntity("maltego.Service", "Tor Exit Node")

                for cve in lookup_response.get("internet_scanner_intelligence", {}).get("cve", []):
                    cve_entity = response.addEntity("maltego.CVE", cve)
                    cve_entity.setLinkLabel("Probes For")

                for item in (
                    lookup_response.get("internet_scanner_intelligence", {}).get("raw_data", {}).get("scan", [])[:10]
                ):
                    port_entity = response.addEntity("maltego.Port", item["port"])
                    port_entity.setLinkLabel("Scans For")

                tag_names = []
                for tag in lookup_response.get("internet_scanner_intelligence", {}).get("tags", [])[:10]:
                    tag_names.append(tag.get("name"))
                    response.addEntity("maltego.Phrase", tag.get("name"))

                lookup_response["link"] = "https://www.greynoise.io/viz/ip/" + str(request.Value)
                # add dynamic properties instead of returning more to the graph
                input_ip.addProperty(
                    fieldName="gn_url",
                    displayName="GreyNoise URL",
                    value=lookup_response["link"],
                    matchingRule="loose",
                )
                input_ip.addProperty(
                    fieldName="gn_last_seen",
                    displayName="GreyNoise last seen",
                    value=lookup_response.get("internet_scanner_intelligence", {}).get("last_seen"),
                    matchingRule="loose",
                )
            else:
                response.addEntity("greynoise.noise", "No Noise Detected")
                response.addUIMessage(f"The IP address {request.Value} hasn't been seen by GreyNoise.")

            add_display_info(
                input_ip,
                lookup_response.get("internet_scanner_intelligence", {}).get("classification"),
                lookup_response.get("internet_scanner_intelligence", {}).get("last_seen"),
                lookup_response.get("link"),
                lookup_response.get("internet_scanner_intelligence", {}).get("actor"),
                tag_names,
            )
        except Exception as e:
            response.addUIMessage(e)
