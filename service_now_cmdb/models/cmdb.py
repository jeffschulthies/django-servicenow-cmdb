import json

import requests
from django.db import models
from requests import TooManyRedirects, HTTPError, ConnectionError, Timeout

from config import settings


class CMDBObjectType(models.Model):
    """
    The type of object you want to model from ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    endpoint = models.CharField(max_length=255, unique=False, blank=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.name)


class CMDBObjectField(models.Model):
    """
    The fields that object contains in ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)
    order = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.name, self.type)


class CMDBObject(models.Model):
    """
    The object you want to model 1:1 to your ServiceNow CMDB object.
    """
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)
    service_now_id = models.CharField(max_length=255)

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.type.name, self.service_now_id)

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
                url="https://{}.service-now.com/api/now/table/{}".format(settings.SERVICE_NOW_DOMAIN, self.type.endpoint),
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

        resp = json.loads(r.text)
        self.service_now_id = resp['result']['sys_id']
        return True

    def put(self, access_token):
        """

        :param access_token:
        :return:
        """

        if not self.service_now_id:
            raise ValueError("There is no ServiceNow ID associated with this object. Try creating the object first.")

        service_now_headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': "application/json"
        }

        try:
            r = requests.put(
                url="https://{}.service-now.com/api/now/table/{}/{}".format(settings.SERVICE_NOW_DOMAIN, self.type.endpoint, str(self.service_now_id)),
                headers=service_now_headers,
                data=json.dumps(self.key_value)
            )
        except (ConnectionError, Timeout, HTTPError, TooManyRedirects) as e:
            raise ValueError("Invalid Endpoint. Error: {}".format(e))

        if r.status_code == 401:
            raise ValueError("Bad Access Token")
        if r.status_code != 200:
            return False

        resp = json.loads(r.text)
        self.service_now_id = resp['result']['sys_id']

        return True

    def get(self, access_token):
        """

        :param access_token:
        :return:
        """

        if not self.service_now_id:
            raise ValueError("There is no ServiceNow ID associated with this object. Try creating the object first.")

        service_now_headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': "application/json"
        }

        try:
            r = requests.get(
                url="https://{}.service-now.com/api/now/table/{}/{}".format(settings.SERVICE_NOW_DOMAIN, self.type.endpoint, str(self.service_now_id)),
                headers=service_now_headers
            )
        except (ConnectionError, Timeout, HTTPError, TooManyRedirects) as e:
            raise ValueError("Invalid Endpoint. Error: {}".format(e))

        if r.status_code == 401:
            raise ValueError("Bad Access Token")
        if r.status_code != 200:
            return False

        return r.text

    def get_field(self, name):
        """

        :param name:
        :return:
        """
        values = CMDBObjectValue.objects.filter(object=self)
        for i in values:
            if i.field.name == name:
                return i
        return None

    def set_field(self, name, value):
        """

        :param name: field name
        :param value:
        :return:
        """
        object_value = CMDBObjectValue.objects.create(object=self, field=name, value=value)
        object_value.save()


class CMDBObjectValue(models.Model):
    """
    The values of the object. The values are limited the the fields of the object type.
    """
    object = models.ForeignKey('CMDBObject', on_delete=models.CASCADE, blank=False)
    field = models.ForeignKey('CMDBObjectField', on_delete=models.CASCADE, blank=False)
    value = models.CharField(max_length=255, unique=False)

    def __str__(self):
        return "{}:{}:{}".format(self.object.id, self.field, self.value)

    def save(self, *args, **kwargs):
        # TODO Add validation. 2 of the same fields should not be able to have the same object.
        super(CMDBObjectValue, self).save(*args, **kwargs)

    @property
    def object_field(self):
        return CMDBObjectField.objects.get(id=self.field)
