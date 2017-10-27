from service_now_cmdb.models.cmdb import CMDBObjectType, CMDBObjectField, CMDBObject, CMDBObjectValue
from service_now_cmdb.tests.models.base_model_test import BaseModelTest
from service_now_cmdb.tests.models.factories import CMDBCompleteType


class TestCMDBObject(BaseModelTest):
    def setUp(self):
        self.cmdb_type = CMDBCompleteType()
        self.cmdb_object_field = CMDBObjectField.objects.get(type=self.cmdb_type)
        self.cmdb_object = CMDBObject.objects.get(type=self.cmdb_type)
        self.cmdb_value = CMDBObjectValue.objects.get(field=self.cmdb_object_field,
                                                      object=self.cmdb_object)

    def tearDown(self):
        CMDBObjectType.objects.all().delete()
        CMDBObjectField.objects.all().delete()
        CMDBObject.objects.all().delete()
        CMDBObjectValue.objects.all().delete()

    def test_field_names(self):
        # TODO: Test ordering and test multiple fields
        self.assertEqual(self.cmdb_object.fields.first(), "subnet")

    def test_key_value(self):
        expected_dict = dict()
        expected_dict['subnet'] = '55.55.55.122'

        self.assertEqual(self.cmdb_object.key_value, expected_dict)

    def test_object_post(self):
        pass

    def test_object_put(self):
        pass

    def test_object_get(self):
        pass

    def test_object_get_field(self):
        pass

    def test_object_set_field(self):
        pass

    def test_object_value_object_field(self):
        pass

    def test_object_relation(self):
        pass

