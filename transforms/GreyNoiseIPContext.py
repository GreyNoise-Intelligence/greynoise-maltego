from maltego_trx.entities import IPAddress, Phrase, ASNumber, Person, Location
from maltego_trx.transform import DiscoverableTransform
import requests

# Created by Adam Maxwell / @catalyst256


class GreyNoiseIPContext(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        headers = {'Accept': 'application/json',
                   'key': request.TransformSettings['GNApiKey']}
        resp = requests.get('https://api.greynoise.io/v2/noise/context/{0}'.format(
            request.Value), params={}, headers=headers)
        if resp.status_code == 200:
            resp = resp.json()
            if resp['seen']:
                response.addEntity(Person, resp['actor'])
                response.addEntity('csr.greynoiseclassification',
                                   resp['classification'])
                for tag in resp['tags']:
                    response.addEntity('csr.greynoisetag', tag)
                if resp.get('metadata'):
                    response.addEntity(ASNumber, str(
                        resp['metadata']['asn']).replace('AS', ''))
                    response.addEntity('maltego.Company',
                                       resp['metadata']['organization'])
                    response.addEntity(Location, '{0},{1}'.format(
                        resp['metadata']['city'], resp['metadata']['country']))

            else:
                response.addUIMessage(
                    "This IP address hasn't been seen by GreyNoise")
        else:
            response.addUIMessage(
                'Whoops we got a {0} status code from the GreyNoise API'.format(str(resp.status_code)))
