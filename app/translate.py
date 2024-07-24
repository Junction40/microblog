import requests
from flask_babel import _
from flask import current_app

def translate(text, source_language, dest_language):
    # Checks if there is a key for the translation service in the config else return error string
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    
    # To authenticate with the service the key and region of the translator resource needs to be provided in the header with the following names:
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'uksouth',
    }
    
    # post() method from the requests package sends an HTTP request with a POST method to the URL given as the first argument
    # Base URL + path for the translation endpoint
    # API version required argument
    # from and to for source and destination languages 
    # Text to translate needs to be given in JSON format
    # returns a response object containing all the details provided by the service
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        '/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}])
    # Check status code is 200 (for successful request)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    # Body of the response has a JSON encoded string translation and since a single text is being translated, it will always be the first element to get
    return r.json()[0]['translations'][0]['text']