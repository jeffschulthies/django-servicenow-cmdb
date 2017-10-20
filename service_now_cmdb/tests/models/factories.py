from datetime import datetime

import factory
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from factory import SubFactory
from factory.fuzzy import FuzzyDateTime
from pytz import UTC

from service_now_cmdb.models import CMDBObject, CMDBObjectField, CMDBObjectValue, CMDBObjectType
from service_now_cmdb.models.token import ServiceNowToken


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    first_name = 'Jeff'
    last_name = 'Schulthies'
    username = factory.LazyAttribute(lambda obj: obj.first_name.lower())
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', 'mamas&papas')
    last_login = factory.LazyFunction(now)


#
#  Token Factory
#
class ServiceNowTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceNowToken

    user = SubFactory(UserFactory)
    created = FuzzyDateTime(datetime(2012, 10, 1, tzinfo=UTC), datetime(2017, 10, 1, tzinfo=UTC))
    scope = "useraccount"
    expires = factory.LazyFunction(now)
    access_token = "sl64frB9Td5m4h68MOwmzNV_NP4muV0zXLi-b3hQSxqWZuOnnXn53U8hiApWk4_gP9rSzWzxm_uVnYnKEtNLJz"
    refresh_token = "Rz2LwLUc-HXskeh5saQNCZ_56yI3lPj_X8w9BU0rbwSNzm1iqfmG8hW8jBFap-6G5A_uDL8dJk8ryrutniSzdw"


class ExpiredServiceNowTokenFactory(ServiceNowTokenFactory):
    expires = FuzzyDateTime(datetime(2012, 10, 1, tzinfo=UTC), datetime(2017, 10, 1, tzinfo=UTC))


class NotExpiredServiceNowTokenFactory(ServiceNowTokenFactory):
    expires = FuzzyDateTime(datetime(9999, 10, 1, tzinfo=UTC), datetime(9999, 10, 1, tzinfo=UTC))


#
#  CMDB Models
#
class CMDBObjectTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CMDBObjectType

    # name = factory.Iterator(["IPAddress", "CIDR"])
    # endpoint = factory.Iterator(['https://companyname.service-now.com/api/now/table/cmdb_ci_ip_network', 'https://companyname.service-now.com/api/now/table/CIDR'])
    name = "IPAddress"
    endpoint = "https://companyname.service-now.com/api/now/table/cmdb_ci_ip_network"


class CMDBObjectFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CMDBObjectField

    type = None
    name = "subnet"


class CMDBObjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CMDBObject

    type = None


class CMDBCompleteType(CMDBObjectTypeFactory):
    @factory.post_generation
    def generate_related_fields(self, create, extracted, **kwargs):
        if not create:
            return
        t_field = CMDBObjectFieldFactory(type=self)
        t_object = CMDBObjectFactory(type=self)
        t_value = CMDBObjectValueFactory(object=t_object, field=t_field)
        return self, t_field, t_object, t_value


class CMDBObjectValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CMDBObjectValue
    object = None
    field = None
    value = "55.55.55.122"
