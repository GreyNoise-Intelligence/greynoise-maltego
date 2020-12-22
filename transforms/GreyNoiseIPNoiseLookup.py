from maltego_trx.entities import IPAddress, Phrase
from maltego_trx.transform import DiscoverableTransform
import requests

# Created by Adam Maxwell / @catalyst256

class GreyNoiseIPNoiseLookup(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        if 'GNAPiKey' in request.TransformSettings:
            api_key = request.TransformSettings['GNApiKey']
        else:
            # enter API key here for local transform
            api_key = ''
        headers = {'Accept': 'application/json',
                   'key': api_key}
        resp = requests.get('https://api.greynoise.io/v2/noise/quick/{0}'.format(
            request.Value), params={}, headers=headers)
        if resp.status_code == 200:
            g = resp.json()
            if g['noise']:
                response.addEntity(
                    'greynoise.noise', 'Noise Detected')
            else:
                response.addEntity('greynoise.noise',
                                   'No Noise Detected')
        else:
            response.addUIMessage(
                'Whoops we got a {0} status code from the GreyNoise API'.format(str(resp.status_code)))
