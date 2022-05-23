from pydoc import cli
from typing import Type
import unittest
from shorty.providers import BaseProvider, BitLy, retryShortenUrlOnOtherProvider, providersTriedAlready
import pytest

def getProvider(provider):
    bp = BaseProvider(provider)
    return bp.getProvider()

class ProvidersTestCase(unittest.TestCase):

    def getProvider(provider):
        bp = BaseProvider(provider)
        return bp.getProvider()

    def test_getNullProviderInstance(self):   
        with self.assertRaises(TypeError) as ex:
            bp = BaseProvider()
            
    def test_getWrongProviderInstance(self):
        bp = BaseProvider("test")
        with self.assertRaises(Exception):
            bp.getProvider()
    
    def test_getCorrectProviderInstance(self):
        provider = getProvider("bit.ly")
        self.assertIs(BitLy, type(provider))
        self.assertEqual(provider.callcount, 0)

    def test_shortenUrlNullValue(self):
        provider = getProvider("bit.ly")   
        with self.assertRaises(Exception) as ex:
            url = provider.shortenUrl("")
        self.assertEqual(ex.exception.description, 'long_url is invalid \n')
        self.assertEqual(ex.exception.code, 500)

    def test_shortenUrlWrongValue(self):
        provider = getProvider("bit.ly")   
        with self.assertRaises(Exception) as ex:
            url = provider.shortenUrl("test")
        self.assertEqual(ex.exception.description, 'long_url is invalid \n')
        self.assertEqual(ex.exception.code, 500)

    def test_shortenUrlCorrectValue(self):
        provider = getProvider("tinyurl.com")   
        url = provider.shortenUrl("test.com")
        self.assertNotEqual(url, "")
        self.assertEqual(provider.callcount, 0)

    def test_shortenUrlRetry(self):
        provider = getProvider("bit.ly")  
        provider.providerurl = "test.com"
        self.assertEqual(provider.callcount, 0)
        url = provider.shortenUrl("test.com")
        self.assertNotEqual(url, "")
        self.assertIn("tinyurl", url)
        self.assertEqual(provider.callcount, 2)

    def test_shortenUrlRetryProvidersNotWorking(self):
        provider = getProvider("tinyurl.com")    
        self.assertEqual(provider.callcount, 0)
        providersTriedAlready.append("bit.ly")
        providersTriedAlready.append("tinyurl.com")
        with self.assertRaises(Exception) as ex:
            retryShortenUrlOnOtherProvider(provider, "test.com")
        self.assertEqual(ex.exception.description, 'No Providers Available')
        self.assertEqual(ex.exception.code, 503)    
