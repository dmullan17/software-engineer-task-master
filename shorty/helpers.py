import json
from flask import abort

def loadProviderInfo():
    try:
        f = open('shorty/providers.json')
    except:
        abort(503, "Error loading providers")
    else:
        providerInfo = json.load(f)
    finally:
        f.close()

    return providerInfo