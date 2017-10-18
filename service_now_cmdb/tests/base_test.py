from unittest import TestCase

from django.contrib.auth.models import User

from service_now_cmdb.models.token import ServiceNowToken


class BaseTest(TestCase):
    def setUp(self):
        pass