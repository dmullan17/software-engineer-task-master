# import unittest
from unittest import mock
from unittest.mock import patch
import pytest
from requests import HTTPError
import json

from shorty.api import create_shortlink

def test_ShortenWithTinyUrl(client):
    test = client.post('/shortlinks')
    print(test)

def test_requestNotJson(client):
    exception = HTTPError(mock.Mock(status=400), "Request body must be in JSON format")

    data = {}
    data['url'] = "test.com"
    json_data = json.dumps(data)

    # response = create_shortlink()

    # mock_get(mock.ANY).raise_for_status.side_effect = exception
    with pytest.raises(ValueError) as ex:
        # client.data = json_data
        shortLink = client.post('/shortlinks', json_data)
        assert ex == exception

    #request not json

    #null request

    #wrong request (more than one)

    #correct request (url and provider)

    #correct request (just url)

