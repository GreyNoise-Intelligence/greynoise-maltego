from maltego_trx.entities import IPAddress, Phrase
from maltego_trx.transform import DiscoverableTransform
import requests

# Created by Adam Maxwell / @catalyst256

class GreyNoiseIPNoiseLookup(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        headers = {'Accept': 'application/json',
                   'key': request.TransformSettings['GNApiKey']}
        resp = requests.get('https://api.greynoise.io/v2/noise/quick/{0}'.format(
            request.Value), params={}, headers=headers)
        if resp.status_code == 200:
            g = resp.json()
            if g['noise']:
                response.addEntity(
                    'csr.greynoiseclassification', 'Noise Detected')
            else:
                response.addEntity('csr.greynoiseclassification',
                                   'No Noise Detected')
        else:
            response.addUIMessage(
                'Whoops we got a {0} status code from the GreyNoise API'.format(str(resp.status_code)))
