from service_now_cmdb.models.cmdb import CMDBObjectType, CMDBObjectField, CMDBObject, CMDBObjectValue
from service_now_cmdb.tests.base_test import BaseTest


class BaseModelTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)

        # ip_address = CMDBObjectType.objects.create(
        #     name="IPAddress",
        #     endpoint="https://athenahealthtest.service-now.com/api/now/table/cmdb_ci_ip_network"
        # )
        #
        # subnet = CMDBObjectField.objects.create(
        #     type=ip_address,
        #     name="subnet"
        # )
        #
        # u_mask = CMDBObjectField.objects.create(type=ip_address, name="u_mask")
        # CMDBObjectField.objects.create(type=ip_address, name="ip_address")
        # CMDBObjectField.objects.create(type=ip_address, name="router")
        # CMDBObjectField.objects.create(type=ip_address, name="u_site_ref")
        # CMDBObjectField.objects.create(type=ip_address, name="u_security_zone")
        # CMDBObjectField.objects.create(type=ip_address, name="name")
        # CMDBObjectField.objects.create(type=ip_address, name="u_number")
        #
        # test_ip = CMDBObject.objects.create(type=ip_address)
        # CMDBObjectValue.objects.create(object=test_ip, field=subnet, value="55.55.55.122")
        # CMDBObjectValue.objects.create(object=test_ip, field=u_mask, value="/32")
        #
        # self.test_ip = test_ip
