import json
import urllib
from urllib.parse import quote_plus

import requests
from django.contrib.auth.models import User
from django.db import models


# @python_2_unicode_compatible
from django.utils import timezone

from django.conf import settings


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
        # Only display the last 24 bits of the token to avoid accidental exposure.
        return "{}".format(self.access_token[-6:])

    def save(self, *args, **kwargs):
        return super(ServiceNowToken, self).save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True

    def get_new_token(self):
        """

        :return:
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

        r = requests.post(url=url, headers=headers, data=payload)

        if r.status_code != 200:
            return False

        data = json.loads(r.text)

        token = ServiceNowToken.objects.get(id=self.id)
        token.scope = data['scope']
        expiration = timezone.now() + timezone.timedelta(seconds=int((data['expires_in'])))
        token.expires = expiration
        token.access_token = str(data['access_token'])
        token.refresh_token = str(data['refresh_token'])
        token.save()
        return True

    @staticmethod
    def get_credentials(username, password):
        """

        :param username:
        :param password:
        :return:
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

        r = requests.post(url=url, headers=headers, data=payload)

        if r.status_code != 200:
            return json.loads(r.text), False
        return json.loads(r.text), True
