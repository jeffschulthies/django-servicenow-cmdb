import json
from datetime import datetime
from unittest.mock import patch, PropertyMock

from django.test import override_settings
from pytz import UTC
from requests import HTTPError, Timeout, TooManyRedirects

from service_now_cmdb.models.token import ServiceNowToken
from service_now_cmdb.tests.models.base_model_test import BaseModelTest
from service_now_cmdb.tests.models.factories import ExpiredServiceNowTokenFactory, NotExpiredServiceNowTokenFactory, \
    ServiceNowTokenFactory


class TestServiceNowToken(BaseModelTest):
    def setUp(self):
        self.token = ExpiredServiceNowTokenFactory.build()
        self.error_response = '{"error_description":"access_denied","error":"server_error"}'
        self.successful_response = '{"access_token":"sl6HfrB9Td5m4hy8MOwmzNV_NP4muV0zXLi-b3hQSxqHZuOnnXn53U8hiZpWk4_gP9rSzWzxm_uVnYnKEtNLJQ","refresh_token":"Qh2LwLUc-HXskeh58aQNCG_56yI3lPj_X8w9BU0rbwSNVmhiqfmG8hW8jBFap-6G5A_uDL8dJkIryrutniSzdw","scope":"useraccount","token_type":"Bearer","expires_in":1799}'
        self.access_token = "sl6HfrB9Td5m4hy8MOwmzNV_NP4muV0zXLi-b3hQSxqHZuOnnXn53U8hiZpWk4_gP9rSzWzxm_uVnYnKEtNLJQ"    # These tokens will be used to test the updating method
        self.refresh_token = "Qh2LwLUc-HXskeh58aQNCG_56yI3lPj_X8w9BU0rbwSNVmhiqfmG8hW8jBFap-6G5A_uDL8dJkIryrutniSzdw"

    def test_str(self):
        self.assertEqual(self.token.__str__(), "EtNLJz")

    def test_is_expired(self):
        self.assertEqual(self.token.is_expired, False)

    def test_is_not_expired(self):
        token = NotExpiredServiceNowTokenFactory.build()
        self.assertEqual(token.is_expired, True)

    def test_empty_token(self):
        token = ServiceNowTokenFactory.build(expires="")
        self.assertEqual(token.is_expired, False)

    @override_settings(SERVICE_NOW_DOMAIN="Test", SERVICE_NOW_CLIENT_ID="Test", SERVICE_NOW_CLIENT_SECRET="test")
    @patch('service_now_cmdb.models.token.ServiceNowToken._update_token')
    @patch('requests.post')
    def test_successful_get_new_token(self, post, update_token_method):
        type(post.return_value).status_code = PropertyMock(return_value=200)
        type(post.return_value).text = PropertyMock(return_value=self.successful_response)
        update_token_method.return_value = True
        self.assertEqual(self.token.get_new_token(), True)

    @override_settings(SERVICE_NOW_DOMAIN="Test", SERVICE_NOW_CLIENT_ID="Test", SERVICE_NOW_CLIENT_SECRET="test")
    @patch('requests.post')
    def test_status_code_error_get_new_token(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=401)
        with self.assertRaises(ValueError):
            self.token.get_new_token()

    @override_settings(SERVICE_NOW_DOMAIN="Test", SERVICE_NOW_CLIENT_ID="Test", SERVICE_NOW_CLIENT_SECRET="test")
    @patch('requests.post')
    def test_request_error_get_new_token(self, post):
        post.side_effect = HTTPError
        with self.assertRaises(ValueError):
            self.token.get_new_token()

        post.side_effect = ConnectionError
        with self.assertRaises(ValueError):
            self.token.get_new_token()

        post.side_effect = Timeout
        with self.assertRaises(ValueError):
            self.token.get_new_token()

        post.side_effect = TooManyRedirects
        with self.assertRaises(ValueError):
            self.token.get_new_token()

    @patch('django.utils.timezone.now')
    def test_update_token(self, time_now):
        time_now.return_value = datetime(2005, 7, 14, 12, 30, 0, tzinfo=UTC)
        token = ServiceNowTokenFactory()
        data = json.loads(self.successful_response)
        token._update_token(data)

        self.assertEqual(token.expires, datetime(2005, 7, 14, 12, 59, 59, tzinfo=UTC))
        self.assertEqual(token.access_token, self.access_token)
        self.assertEqual(token.refresh_token, self.refresh_token)
        self.assertEqual(token.scope, "useraccount")
        pass

    @override_settings(SERVICE_NOW_DOMAIN="Test", SERVICE_NOW_CLIENT_ID="Test", SERVICE_NOW_CLIENT_SECRET="test")
    @patch('requests.post')
    def test_successful_get_credentials(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=200)
        type(post.return_value).text = PropertyMock(return_value=self.successful_response)
        text, value = ServiceNowToken.get_credentials("jeff", "test")
        self.assertEqual(text, json.loads(self.successful_response))
        self.assertEqual(value, True)

    @override_settings(SERVICE_NOW_DOMAIN="Test", SERVICE_NOW_CLIENT_ID="Test", SERVICE_NOW_CLIENT_SECRET="test")
    @patch('requests.post')
    def test_error_get_credentials(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=401)
        type(post.return_value).text = PropertyMock(return_value=self.error_response)
        text, value = ServiceNowToken.get_credentials("jeff", "test")
        self.assertEqual(text, json.loads(self.error_response))
        self.assertEqual(value, False)
