import getpass

from django.contrib.contenttypes.models import ContentType

from config import settings
from service_now_cmdb.models import CMDBObjectType, CMDBObject, CMDBObjectValue, ServiceNowToken, CMDBObjectField


class SNCMDBHandler:

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.domain = settings.SERVICE_NOW_DOMAIN
        self.client_id = settings.SERVICE_NOW_CLIENT_ID
        self.client_secret = settings.SERVICE_NOW_CLIENT_SECRET
        self.token = None

    def create_credentials(self, username):
        """
        If the user is not associated with sn credentials.

        :param username:
        :return:
        """
        password = getpass.getpass(prompt='Enter your password: ')
        data = ServiceNowToken.get_credentials(username, password)
        self.token = ServiceNowToken.create_token(data, self.user)
        return True

    def get_credentials(self):
        """

        :return:
        """
        self.token = ServiceNowToken.objects.get(user=self.user)
        return True

    @staticmethod
    def create_cmdb_object_type(model, endpoint):
        """

        :param model:
        :param endpoint:
        :return:
        """
        model = ContentType.objects.get_for_model(model)
        cmdb_object_type = CMDBObjectType.objects.create(
            name=model.name,
            endpoint=endpoint,
            content_type=model
        )
        return cmdb_object_type

    @staticmethod
    def update_cmdb_object_type(model, endpoint):
        """

        :param model:
        :param endpoint:
        :return:
        """
        model = ContentType.objects.get_for_model(model)
        cmdb_object_type = CMDBObjectType.objects.get(
            name=model.name,
            content_type=model
        )
        cmdb_object_type.endpoint = endpoint
        cmdb_object_type.save()
        return cmdb_object_type

    @staticmethod
    def create_cmdb_object_field(name, cmdb_type, order):
        """

        :param name:
        :param cmdb_type:
        :param order:
        :return:
        """
        cmdb_object_field = CMDBObjectField.objects.create(
            name=name,
            type=cmdb_type,
            order=order
        )
        return cmdb_object_field

    @staticmethod
    def update_cmdb_object_field(name, cmdb_type, new_name=None, order=None):
        """
        Note: The ServiceNow object will need to be updated.
        :param name:
        :param cmdb_type:
        :param new_name:
        :param order:
        :return:
        """
        cmdb_object_field = CMDBObjectField.objects.get(name=name, type=cmdb_type)
        if new_name:
            cmdb_object_field.name = new_name
        if order:
            cmdb_object_field.order = order
        cmdb_object_field.save()

        return cmdb_object_field

    @staticmethod
    def create_cmdb_object_value(cmdb_object, cmdb_field, value):
        """

        :param cmdb_object:
        :param cmdb_field:
        :param value:
        :return:
        """
        cmdb_object_value = CMDBObjectValue.objects.create(
            object=cmdb_object,
            field=cmdb_field,
            value=value
        )
        return cmdb_object_value

    @staticmethod
    def update_cmdb_object_value(cmdb_object, cmdb_field, value):
        """

        :param cmdb_object:
        :param cmdb_field:
        :param value:
        :return:
        """
        cmdb_object_value = CMDBObjectValue.objects.get(
            object=cmdb_object,
            field=cmdb_field
        )
        cmdb_object_value.value = value
        cmdb_object_value.save()
        return cmdb_object_value

    def create_cmdb_object(self, model_object):
        """

        :param model_object:
        :return:
        """
        model = ContentType.objects.get_for_model(model_object)
        cmdb_object_type = CMDBObjectType.objects.get(content_type=model.id)

        cmdb_object = CMDBObject.objects.create(
            type=cmdb_object_type,
            object_id=model_object.id
        )

        cmdb_object.post(self.token.access_token)
        return cmdb_object

    @staticmethod
    def does_cmdb_object_exists(model_object):
        """
        Return true or false depending if the model has a cmdb object

        :param model_object:
        :return:
        """

        model = ContentType.objects.get_for_model(model_object)
        cmdb_object_type = CMDBObjectType.objects.get(content_type=model.id)
        object_id = model_object.id

        cmdb_object_exists = CMDBObject.objects.filter(
            type=cmdb_object_type,
            object_id=object_id
        ).exists()

        if cmdb_object_exists:
            return True
        return False

    def update_cmdb_object(self, model_object):
        """
        Usage: whenever a model is updated add this command

        :param model_object:
        :return:
        """
        model = ContentType.objects.get_for_model(model_object)
        cmdb_object_type = CMDBObjectType.objects.get(content_type=model.id)
        object_id = model_object.id

        cmdb_object = CMDBObject.objects.get(
            type=cmdb_object_type,
            object_id=object_id
        )

        cmdb_object.put(self, self.token)

        return True
