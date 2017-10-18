import logging

from django.test import TestCase

from service_now_cmdb.models.cmdb import CMDBObjectType, CMDBObjectField, CMDBObject, CMDBObjectValue
from service_now_cmdb.tests.models.base_model_test import BaseModelTest

LOGGER = logging.getLogger(__name__)


class TestCMDBObject(BaseModelTest):
    def test_object_relation(self):
        pass

    def test_object_post(self):
        pass

    def test_object_put(self):
        pass


class TestCMDBObjectType(TestCase):
    pass


class TestCMDBObjectField(TestCase):
    pass


class TestCMDBObjectValue(TestCase):
    pass
