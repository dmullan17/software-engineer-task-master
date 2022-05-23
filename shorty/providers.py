from flask import jsonify, abort
import requests
import time
from shorty.helpers import loadProviderInfo

#gotten from https://stackoverflow.com/a/8313042/10495793
#assertion error is raised if child classes dont implement parents method
def overrides(base_class):
    def overrider(method):
        assert(method.__name__ in dir(base_class))
        return method
    return overrider

providersTriedAlready = []

class BaseProvider:
    def __init__(self, name):
        self.providername = name

    def getProvider(self):
        # this code needs updated if a new provider is added to providers.json
        if self.providername == "bit.ly":
            return BitLy(self.providername)
        elif self.providername  == "tinyurl.com":
            return TinyUrl(self.providername)
        else:
            abort(500, "Provider given is not valid")

    def shortenUrl():
        return   

class BitLy(BaseProvider):
    def __init__(self, name):
        super().__init__(name)
        providerInfo = loadProviderInfo()
        self.callcount = 0

        #validating that values needed for request exist in providers.json
        if not all(key in providerInfo for key in ("providerurl", "authtoken", "groupguid")):
            errorString = "{0} instance is missing config setting(s): ".format(name)
            if "providerurl" not in providerInfo[name]:
                errorString += "providerurl "
            if "authtoken" not in providerInfo[name]:
                errorString += "authtoken "
            if "groupguid" not in providerInfo[name]:
                errorString += "groupguid "
            abort(503, errorString)
        else:
            self.authtoken = providerInfo[name]["authtoken"]
            self.groupguid = providerInfo[name]["groupguid"]
            self.providerurl = providerInfo[name]["providerurl"]

    @overrides(BaseProvider)
    def shortenUrl(self, url):
        try:
            head = {"Authorization": "Bearer " + self.authtoken}
            data = jsonify({"long_url": "https://" + url, "domain": self.providername, "group_guid": self.groupguid })
            r = requests.post(self.providerurl, json=data.json, headers=head)
        except Exception as e:
            #todo log error details
            #retry method 2 more times before using other available providers to shorten url
            retriedUrl = retry(self, url)
            if self.callcount == 2:
                return retriedUrl
        else:
            if "errors" not in r.json():
                return r.json()["link"]
            else:
                for i in r.json()["errors"]:
                    errorString = "{0} is {1} \n".format(i['field'], i['error_code'])
                abort(500, errorString)


class TinyUrl(BaseProvider):
    def __init__(self, name):
        super().__init__(name)
        providerInfo = loadProviderInfo()
        self.callcount = 0

        #validating that values needed for request exist in providers.json
        if "providerurl" not in providerInfo[name]:
            abort(503, "{0} instance is missing config setting: providerurl".format(name))
        else:
            self.providerurl = providerInfo[name]["providerurl"]

    @overrides(BaseProvider)
    def shortenUrl(self, url):
        try:
            r = requests.get(self.providerurl + url)
        except Exception as e:
            #todo log error details
            #retry method 2 more times before using other available providers to shorten url 
            retriedUrl = retry(self, url)
            if self.callcount == 2:
                return retriedUrl
        else:
            return r.text

def retry(self, url):
    if self.callcount < 2:
        time.sleep(1)
        self.callcount += 1 
        return self.shortenUrl(url)
    else:
        otherProvidersUrl = retryShortenUrlOnOtherProvider(self, url)
        return otherProvidersUrl

def retryShortenUrlOnOtherProvider(provider, url):
    providerInfo = loadProviderInfo()

    global providersTriedAlready
    if provider.providername not in providersTriedAlready:
        providersTriedAlready.append(provider.providername)

    for i in providerInfo:
        if i != provider.providername and i not in providersTriedAlready:
            bp = BaseProvider(i)
            instance = bp.getProvider()
            break

    #tried all providers
    if 'instance' not in locals():
        abort(503, "No Providers Available")

    return instance.shortenUrl(url)