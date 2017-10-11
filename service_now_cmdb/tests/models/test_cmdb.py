import logging

from django.test import TestCase

from service_now_cmdb.models.cmdb import CMDBObjectType, CMDBObjectField, CMDBObject, CMDBObjectValue
from service_now_cmdb.tests.models.base_model_test import BaseModelTest

LOGGER = logging.getLogger(__name__)


class TestCMDBObject(BaseModelTest):
    def test_object_relation(self):
        values = CMDBObjectValue.objects.filter(object=self.test_ip).values_list('value', flat=True)
        self.assertIn("55.55.55.122", values)
        self.assertIn("/32", values)


class TestCMDBObjectType(TestCase):
    pass


class TestCMDBObjectField(TestCase):
    pass


class TestCMDBObjectValue(TestCase):
    pass
