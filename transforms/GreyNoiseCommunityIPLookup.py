from greynoise import GreyNoise
from maltego_trx.entities import Person
from maltego_trx.transform import DiscoverableTransform


class GreyNoiseCommunityIPLookup(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        api_key = request.TransformSettings["GNApiKey"]
        api_client = GreyNoise(
            api_key=api_key,
            integration_name="maltego-community-v1.0.0",
            offering="community",
        )
        try:
            resp = api_client.ip(request.Value)
            if resp["noise"]:
                response.addEntity("greynoise.noise", "Noise Detected")
                response.addEntity(Person, resp["name"])
                response.addEntity("greynoise.classification", resp["classification"])
                response.addEntity("greynoise.last_seen", resp["last_seen"])
                response.addEntity("greynoise.link", resp["link"])
            elif resp["riot"]:
                if resp["riot"]:
                    response.addEntity("greynoise.riot", "Benign Service Detected")
                    response.addEntity(Person, resp["name"])
                    response.addEntity("greynoise.last_seen", resp["last_seen"])
                    response.addEntity("greynoise.link", resp["link"])
            else:
                response.addEntity("greynoise.noise", "No Noise Detected")
                response.addUIMessage("This IP address hasn't been seen by GreyNoise")
        except Exception as e:
            response.addUIMessage(e)
