from greynoise import GreyNoise
from maltego_trx.entities import ASNumber, Person, Location
from maltego_trx.transform import DiscoverableTransform

class GreyNoiseIPContext(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        api_key = request.TransformSettings['GNApiKey']
        api_client = GreyNoise(api_key=api_key, integration_name="maltego-v1.0.0-beta")
        try:
            resp = api_client.ip(request.Value)
            if resp['seen']:
                response.addEntity(Person, resp['actor'])
                response.addEntity('greynoise.classification',
                                   resp['classification'])
                for tag in resp['tags']:
                    response.addEntity('greynoise.tag', tag)
                if resp.get('metadata'):
                    response.addEntity(ASNumber, str(
                        resp['metadata']['asn']).replace('AS', ''))
                    response.addEntity('maltego.Company',
                                       resp['metadata']['organization'])
                    response.addEntity(Location, '{0},{1}'.format(
                        resp['metadata']['city'], resp['metadata']['country']))

            else:
                response.addEntity('greynoise.noise',
                                   'No Noise Detected')
                response.addUIMessage(
                    "This IP address hasn't been seen by GreyNoise")
        except Exception as e:
            response.addUIMessage(
                e)