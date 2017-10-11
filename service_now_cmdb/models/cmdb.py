import json
from collections import defaultdict

import requests
from django.db import models
from requests import TooManyRedirects, HTTPError, ConnectionError, Timeout


class CMDBObjectType(models.Model):
    """
    The type of object you want to model from ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    endpoint = models.CharField(max_length=255, unique=False, blank=False)


class CMDBObjectField(models.Model):
    """
    The fields that object contains in ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)


class CMDBObject(models.Model):
    """
    The object you want to model 1:1 to your ServiceNow CMDB object.
    """
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)

    def post(self, access_token):
        """

        :param access_token:
        :return:
        """
        service_now_headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': "application/json"
        }

        try:
            r = requests.post(
                url=self.type.endpoint,
                headers=service_now_headers,
                data=json.dumps(self.key_value)
            )
        except (ConnectionError, Timeout, HTTPError, TooManyRedirects) as e:
            raise ValueError("Invalid Endpoint. Error: {}".format(e))

        if r.status_code == 401:
            raise ValueError("Bad Access Token")
        if r.status_code != 201:
            # Invalid Input
            return False
        return True

    @property
    def fields(self):
        """

        :return: QuerySet
        """
        values = CMDBObjectValue.objects.filter(object=self).values_list('field_id')
        field_names = CMDBObjectField.objects.filter(pk__in=values).values_list('name', flat=True)
        return field_names

    @property
    def key_value(self):
        """

        :return: Dictionary
        """
        values = CMDBObjectValue.objects.filter(object=self).values()
        d = dict()
        for i in values:
            object_field = CMDBObjectField.objects.get(id=i['field_id'])
            field_name = object_field.name
            d[field_name] = i['value']
        return d


class CMDBObjectValue(models.Model):
    """
    The values of the object. The values are limited the the fields of the object type.
    """
    object = models.ForeignKey('CMDBObject', on_delete=models.CASCADE, blank=False)
    field = models.ForeignKey('CMDBObjectField', on_delete=models.CASCADE, blank=False)
    value = models.CharField(max_length=255, unique=False)
