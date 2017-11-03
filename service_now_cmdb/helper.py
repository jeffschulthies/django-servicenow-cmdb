from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .models import CMDBObjectType, CMDBObject, CMDBObjectValue, ServiceNowToken, CMDBObjectField
import service_now_cmdb.function_mapping as store


class SNCMDBHandler:
    def __init__(self, user):
        self.user = user
        self.domain = settings.SERVICE_NOW_DOMAIN
        self.client_id = settings.SERVICE_NOW_CLIENT_ID
        self.client_secret = settings.SERVICE_NOW_CLIENT_SECRET
        self.token = None

    def create_credentials(self, username, password):
        """
        If the user is not associated with sn credentials.

        Args:
            username:
            password:

        Returns:

        """
        data = ServiceNowToken.get_credentials(username, password)
        self.token = ServiceNowToken.create_token(data, self.user)
        return True

    def get_credentials(self):
        """

        Returns:

        """
        try:
            self.token = ServiceNowToken.objects.get(user=self.user)
        except ObjectDoesNotExist:
            return False
        return True

    @staticmethod
    def create_cmdb_object_type(model, endpoint):
        """

        Args:
            model:
            endpoint:

        Returns:

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
        Update the model endpoint

        Args:
            model:
            endpoint:

        Returns:

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
    def create_cmdb_object_field(name, cmdb_type, order, model_field="", model_function=""):
        """

        Args:
            name:
            cmdb_type:
            order:
            model_field:
            model_function:

        Returns:

        """

        if model_field and model_function:
            raise ValueError("model_field and model_function are both defined. You may only set one of them.")
        if not model_field and not model_function:
            raise ValueError("Neither model_field nor model_function are defined. You may must set one of them.")

        cmdb_object_field = CMDBObjectField.objects.create(
            name=name,
            type=cmdb_type,
            model_field=model_field,
            model_function=model_function,
            order=order
        )
        return cmdb_object_field

    @staticmethod
    def update_cmdb_object_field(name, cmdb_type, new_name=None, order=None, model_field=None, model_function=None):
        """

        Args:
            name:
            cmdb_type:
            new_name:
            order:
            model_field:
            model_function:

        Returns:

        """
        cmdb_object_field = CMDBObjectField.objects.get(name=name, type=cmdb_type)
        if new_name:
            cmdb_object_field.name = new_name
        if order:
            cmdb_object_field.order = order
        if model_field:
            cmdb_object_field.model_field = model_field
        if model_function:
            cmdb_object_field.model_function = model_function

        cmdb_object_field.save()

        return cmdb_object_field

    @staticmethod
    def create_cmdb_object_value(cmdb_object, cmdb_field, value):
        """

        Args:
            cmdb_object:
            cmdb_field:
            value:

        Returns:

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

        Args:
            cmdb_object:
            cmdb_field:
            value:

        Returns:

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

        Args:
            model_object:

        Returns:

        """

        model = ContentType.objects.get_for_model(model_object)
        cmdb_object_type = CMDBObjectType.objects.get(content_type=model.id)

        if self.does_cmdb_object_exist(model_object):
            raise ValueError("This object already has a model. Try using the update_cmdb_object_value function.")

        cmdb_object = CMDBObject.objects.create(
            type=cmdb_object_type,
            object_id=model_object.id
        )

        # Check the associated fields to the object
        object_fields = cmdb_object.fields

        for field in object_fields:
            if field.model_field:
                # Create value object for the field where the field is the ServiceNow field
                # model_field is the field associated the the ServiceNow field
                self.create_cmdb_object_value(cmdb_object, field, getattr(model_object, field.model_field))
            elif field.model_function:
                # Pass a function instead when the relationship is not directly 1:1
                func = getattr(store, field.model_function)
                self.create_cmdb_object_value(cmdb_object, field, func(model_object))
            else:
                raise AttributeError("The field {} does not a contain a model_field or model function".format(field))

        cmdb_object.post(self.token.access_token)
        return cmdb_object

    @staticmethod
    def does_cmdb_object_exist(model_object):
        """
        Return true or false depending if the model has a cmdb object

        Args:
            model_object:

        Returns:

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

        Args:
            model_object:

        Returns:

        """
        model = ContentType.objects.get_for_model(model_object)
        cmdb_object_type = CMDBObjectType.objects.get(content_type=model.id)
        object_id = model_object.id

        try:
            cmdb_object = CMDBObject.objects.get(
                type=cmdb_object_type,
                object_id=object_id
            )
        except CMDBObject.DoesNotExist:
            raise "You must create a cmdb_object first."

        # Check the associated fields to the object
        object_fields = cmdb_object.fields

        for field in object_fields:
            if field.model_field:
                # Create value object for the field where the field is the ServiceNow field
                # model_field is the field associated the the ServiceNow field
                self.create_cmdb_object_value(cmdb_object, field, getattr(model_object, field.model_field))
            elif field.model_function:
                # Pass a function instead when the relationship is not directly 1:1
                func = getattr(store, field.model_function)
                self.create_cmdb_object_value(cmdb_object, field, func(model_object))
            else:
                raise AttributeError("The field {} does not a contain a model_field or model function".format(field))

        cmdb_object.put(self.token.access_token)
        return cmdb_object
