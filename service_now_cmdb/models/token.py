import json
import urllib
import requests
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.conf import settings
from requests import Timeout, HTTPError, TooManyRedirects
from urllib.parse import quote_plus


class ServiceNowToken(models.Model):
    """
    Stub
    """
    user = models.OneToOneField(User)
    created = models.DateTimeField(auto_now_add=True)
    scope = models.CharField(max_length=255, unique=False)
    expires = models.DateTimeField(blank=True, null=False)
    access_token = models.CharField(max_length=255, unique=False)
    refresh_token = models.CharField(max_length=255, unique=False)

    class Meta:
        default_permissions = []

    def __str__(self):
        # Only display the last 6 bits of the token to avoid accidental exposure.
        return "{}".format(self.access_token[-6:])

    @property
    def is_expired(self):
        """

        Returns:

        """
        if self.expires == "" or self.expires is None or timezone.now() > self.expires:
            return True
        return False

    def _update_token(self, data):
        """
        Used by the get new token method

        Args:
            data:

        Returns:

        """

        self.scope = data['scope']
        expiration = timezone.now() + timezone.timedelta(seconds=int((data['expires_in'])))
        self.expires = expiration
        self.access_token = str(data['access_token'])
        self.refresh_token = str(data['refresh_token'])
        self.save()
        return True

    def get_new_token(self):
        """

        Returns: False if the endpoint
        Raises ValueError: This can be caused by multiple errors.

        """

        url = "https://{}.service-now.com/oauth_token.do".format(settings.SERVICE_NOW_DOMAIN)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'refresh_token',
            'client_id': '{}'.format(settings.SERVICE_NOW_CLIENT_ID),
            'refresh_token': self.refresh_token
        }

        payload = urllib.parse.urlencode(data, quote_via=quote_plus)
        payload = payload + "&client_secret={}".format(settings.SERVICE_NOW_CLIENT_SECRET)

        try:
            r = requests.post(url=url, headers=headers, data=payload)
        except (ConnectionError, Timeout, HTTPError, TooManyRedirects) as e:
            raise ValueError("Invalid ServiceNow Endpoint. Check SERVICE_NOW_DOMAIN, SERVICE_NOW_CLIENT_ID, "
                             "or SERVICE_NOW_CLIENT_SECRET in the settings file.".format(e))

        if r.status_code != 200:
            raise ValueError("Something went wrong. Check SERVICE_NOW_DOMAIN, SERVICE_NOW_CLIENT_ID, "
                             "or SERVICE_NOW_CLIENT_SECRET in the settings file. ")

        data = json.loads(r.text)

        self._update_token(data)
        print(self.access_token)
        return True

    @staticmethod
    def create_token(data, user):
        """
        Create a token from a json object created from the ServiceNow response.

        Args:
            data:
            user:

        Returns:

        """

        expiration = timezone.now() + (timezone.timedelta(seconds=int(data['expires_in'])))
        try:
            sn_token = ServiceNowToken.objects.get(user=user)
            sn_token.scope = data['scope']
            sn_token.access_token = data['access_token']
            sn_token.refresh_token = data['refresh_token']
            sn_token.expires = expiration
            sn_token.save()
        except ObjectDoesNotExist:
            sn_token = ServiceNowToken(user=user,
                                       scope=data['scope'],
                                       access_token=data['access_token'],
                                       refresh_token=data['refresh_token'],
                                       expires=expiration
                                       )
            sn_token.save()
        return sn_token

    @staticmethod
    def get_credentials(username, password):
        """

        Args:
            username:
            password:

        Returns:

        """
        url = "https://{}.service-now.com/oauth_token.do".format(settings.SERVICE_NOW_DOMAIN)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'password',
            'client_id': '{}'.format(settings.SERVICE_NOW_CLIENT_ID),
            'username': username,
            'password': password
         }

        payload = urllib.parse.urlencode(data, quote_via=quote_plus)
        payload = payload + "&client_secret={}".format(settings.SERVICE_NOW_CLIENT_SECRET)

        try:
            r = requests.post(url=url, headers=headers, data=payload)
        except (ConnectionError, Timeout, HTTPError, TooManyRedirects) as e:
            raise ValueError("Invalid ServiceNow Endpoint. Check SERVICE_NOW_DOMAIN, SERVICE_NOW_CLIENT_ID, "
                             "or SERVICE_NOW_CLIENT_SECRET in the settings file.".format(e))
        try:
            r.raise_for_status()
        except:
            raise ValueError("Invalid Credentials.")
        return json.loads(r.text)
