import json

import requests
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from requests import TooManyRedirects, HTTPError, ConnectionError, Timeout

from django.conf import settings


class CMDBObjectType(models.Model):
    """
    The type of object you want to model from ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    endpoint = models.CharField(max_length=255, unique=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.id, self.name)


class CMDBObjectField(models.Model):
    """
    The fields that object contains in ServiceNow.
    """
    name = models.CharField(max_length=255, unique=False, blank=False)
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)
    model_field = models.CharField(max_length=255, unique=False, blank=True)
    model_function = models.CharField(max_length=255, unique=False, blank=True)
    order = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.name, self.type)

    def clean(self):
        if CMDBObjectField.objects.filter(name=self.name, type=self.type).exists():
            raise ValidationError("There already exists a field '{}' associated with this object type '{}'.".format(self.name, self.type.name))
        if CMDBObjectField.objects.filter(name=self.model_field, type=self.type).exists():
            raise ValidationError("There already exists a model field '{}' associated with this object type '{}'.".format(self.model_field, self.type.name))
        if self.model_field and self.model_function:
            raise ValidationError("Model field and model function can not both be defined")
        if not self.model_field and not self.model_function:
            raise ValidationError("Model field and model function can not both be empty")

    def save(self, *args, **kwargs):
        self.clean()
        super(CMDBObjectField, self).save(*args, **kwargs)


class CMDBObject(models.Model):
    """
    The object you want to model 1:1 to your ServiceNow CMDB object.
    """
    type = models.ForeignKey('CMDBObjectType', on_delete=models.CASCADE, blank=False)
    service_now_id = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.type.name, self.service_now_id)

    def save(self, *args, **kwargs):
        super(CMDBObject, self).save(*args, **kwargs)

    @property
    def fields(self):
        """

        Returns:

        """
        fields = CMDBObjectField.objects.filter(type=self.type)
        return fields

    @property
    def field_names(self):
        """

        Returns:

        """
        field_names = CMDBObjectField.objects.filter(type=self.type).values_list('name', flat=True)
        return field_names

    @property
    def non_empty_field_names(self):
        """

        Returns:

        """
        values = CMDBObjectValue.objects.filter(object=self).values_list('field_id')
        field_names = CMDBObjectField.objects.filter(pk__in=values).values_list('name', flat=True)
        return field_names

    @property
    def key_value(self):
        """

        Returns:

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

        Args:
            access_token:

        Returns:

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
        self.save()
        return True

    def put(self, access_token):
        """

        Args:
            access_token:

        Returns:

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

        return True

    def get(self, access_token):
        """

        Args:
            access_token:

        Returns:

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

        Args:
            name:

        Returns:

        """
        values = CMDBObjectValue.objects.filter(object=self)
        for i in values:
            if i.field.name == name:
                return i
        return None

    def set_field(self, name, value):
        """

        Args:
            name:
            value:

        Returns:

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
        super(CMDBObjectValue, self).save(*args, **kwargs)

    @property
    def object_field(self):
        return CMDBObjectField.objects.get(id=self.field)
