from greynoise import GreyNoise
from maltego_trx.transform import DiscoverableTransform

class GreyNoiseIPNoiseLookup(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        api_key = request.TransformSettings['GNApiKey']
        api_client = GreyNoise(api_key=api_key, integration_name="maltego-v1.0.0-beta")
        try:
            resp = api_client.quick(request.Value)
            if resp and resp[0]['noise']:
                response.addEntity(
                    'greynoise.noise', 'Noise Detected')
            else:
                response.addEntity('greynoise.noise',
                                   'No Noise Detected')
        except Exception as e:
            response.addUIMessage(
                e)
