from flask import Blueprint, jsonify, request, abort
from shorty.helpers import loadProviderInfo


api = Blueprint('api', __name__)


@api.route('/shortlinks', methods=['POST'])
def create_shortlink():
    providerInfo = loadProviderInfo()

    if request.is_json:
        content = request.get_json()
        if "url" in content:
            url = content["url"]
            if len(providerInfo) > 0:
                if "provider" in content:
                    # ensures that the provider given has info stored in providers.json
                    if content["provider"] in providerInfo.keys():
                        provider = content["provider"]
                    else:
                        abort(400, "Invalid Provider supplied")
                else:
                    #assign provider if 'isdefault' is set to true from provider connection info
                    for i in providerInfo.keys():
                        if "isdefault" in providerInfo[i]:
                            if providerInfo[i]["isdefault"] == True:
                                provider = i
                                break

                    #if no providers have 'isdefault' set to true, set first in json
                    if 'provider' not in locals():
                        provider = next(iter(providerInfo.keys()))
            else:
                abort(503, "No Providers Available")
        else:
            abort(400, "URL not specified")
    else:
        abort(400, "Request body must be in JSON format")

    providerInstance = getProviderInstance(provider)
    shortenedUrl = providerInstance.shortenUrl(url)

    return jsonify({"link": shortenedUrl, "url": url})

def getProviderInstance(provider):
    from shorty.providers import BaseProvider
    bp = BaseProvider(provider)
    instance = bp.getProvider()
    return instance

@api.route('/shortlinkstest', methods=['GET'])
def test():
    # return jsonify({})
    return "test";
