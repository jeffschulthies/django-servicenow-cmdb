from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .models import CMDBObjectType, CMDBObject, CMDBObjectValue, ServiceNowToken, CMDBObjectField
from . import field_mapping as store


class SNCMDBHandler:
    """
    SNCMDB Handler. Provides a wrapper to interact with the cmdb models.
    """
    def __init__(self, user):
        self.user = user
        self.domain = settings.SERVICE_NOW_DOMAIN
        self.client_id = settings.SERVICE_NOW_CLIENT_ID
        self.client_secret = settings.SERVICE_NOW_CLIENT_SECRET
        self.token = None

    def create_credentials(self, username, password):
        """
        Requests a SN token using the user credentials and stores it in the database.

        Args:
            username: SN Username. (Depends on your organization)
            password: SN Password.

        Returns:
            bool: True if successful, False otherwise.
        """

        data = ServiceNowToken.get_credentials(username, password)
        self.token = ServiceNowToken.create_token(data, self.user)
        return True

    def get_credentials(self):
        """
        Retrieves the SN Token. This function checks if the user has a token in the database.
        It refreshes the token if it is invalid.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.token = ServiceNowToken.objects.get(user=self.user)
        except ObjectDoesNotExist:
            return False

        if self.token.is_expired:
            self.token.get_new_token()
        return True

    @staticmethod
    def create_cmdb_object_type(model, endpoint):
        """
        Creates a CMDB Object Type. The type of object you want to model from ServiceNow.

        Args:
            model: The name of Django model you want to map.
            endpoint: ServiceNow API Endpoint. This is the table name in the endpoint. https://[instance].service-now.com/api/now/table/[table_name]

        Returns:
            CMDBObjectType that was created.


        Example:
            >>> from test.models import IPAddress
            >>> cmdb_type = handler.create_cmdb_object_type(IPAddress, "cmdb_ci_ip_network")

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
        Update a CMDB Object Type.

        Args:
            model: The name of Django model you want to map.
            endpoint: ServiceNow API Endpoint. This is the table name in the endpoint. https://[instance].service-now.com/api/now/table/[table_name]

        Returns:
            CMDBObjectType that was created.

        Example:
            >>> from test.models import IPAddress
            >>> cmdb_type = handler.update_cmdb_object_type(IPAddress, "new_cmdb_ci_ip_network")
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
        Creates a CMDB Object Field. This is the field of the SN object you want map to a Django model.

        Args:
            name (str): The name of the ServiceNow Object field.
            cmdb_type (CMDBObjectType): The type of ServiceNow object.
            order (int): This will be used for ordering results in the future. This is currently not implemented.
            model_field (str): A model can either have a model_field or model_function not both. A model field is used when the Django model and ServiceNow object is a 1:1 mapping. The field refers to the field name of the model in Django models file.
            model_function (str): The name of the function found in field_mapping.py. A model function is used when we must do some processing before we do the mapping. It passes the entire Django model to the function in field mappings file.

        Returns:
            CMDBObjectField that was created.

        Example
        -------
        >>> from test.models import IPAddress
        >>> cmdb_type = handler.create_cmdb_object_type(IPAddress, "cmdb_ci_ip_network")
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
        Updates a CMDB Object Field.

        Args:
            name: The name of the ServiceNow Object field.
            cmdb_type: The type of ServiceNow object.
            order: This will be used for ordering results in the future. This is currently not implemented.
            model_field: A model can either have a model_field or model_function not both. A model field is used when the Django model and ServiceNow object is a 1:1 mapping. The field refers to the field name of the model in Django models file.
            model_function: The name of the function found in field_mapping.py. A model function is used when we must do some processing before we do the mapping. It passes the entire Django model to the function in field mappings file.

        Returns:
            CMDBObjectField that was updated.
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
        Create a value for the object. The fields are only tracked if defined in CMDBObjectField.

        Args:
            cmdb_object (CMDBObject): The object that is being tracked
            cmdb_field (CMDBObjectField) : The field that is being tracked
            value (str): The value that will be associated with these two fields.

        Returns:
            CMDBObjectValue that was created.

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
        Update a value for the object. The fields are only tracked if defined in CMDBObjectField.

        Args:
            cmdb_object (CMDBObject): The object that is being tracked
            cmdb_field (CMDBObjectField) : The field that is being tracked
            value (str): The value that will be associated with these two fields.

        Returns:
            CMDBObjectValue that was updated.

        """
        try:
            cmdb_object_value = CMDBObjectValue.objects.get(
                object=cmdb_object,
                field=cmdb_field
            )
        except CMDBObjectValue.MultipleObjectsReturned:
            # TODO: Replace with a log
            print("Fatal error")

        cmdb_object_value.value = value
        cmdb_object_value.save()
        return cmdb_object_value

    def create_cmdb_object(self, model_object):
        """
        Create a CMDBObject. These objects are created to allow us to track which objects are in SN.

        Args:
            model_object: Any Django object.

        Returns:
            CMDBObject that was created.

        Raises:
              ValueError: When there is an issue with the models
              AttributeError: Occurs when a field does not contain a mapping field or function.

        Example:
            >>> from test.models import IPAddress
            >>> cmdb_type = handler.create_cmdb_object_type(IPAddress, "cmdb_ci_ip_network")
            >>> ip_to_insert = IPAddress.objects.create()
            >>> create_cmdb_object(ip_to_insert)
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
                if func is not None:
                    self.create_cmdb_object_value(cmdb_object, field, func(model_object))
                else:
                    # Log This
                    print("Model function field is incorrect")
            else:
                raise AttributeError("The field {} does not a contain a model_field or model function".format(field))
        if not cmdb_object.post(self.token.access_token):
            # Log This
            raise ValueError("Something happened with the model")
        return cmdb_object

    @staticmethod
    def does_cmdb_object_exist(model_object):
        """
        This is used to determine if a CMDBObject exists for a model object.

        Args:
            model_object: Any Django object.

        Returns:
            bool: True if successful, False otherwise.

        Example:
            >>> from test.models import IPAddress
            >>> cmdb_type = handler.create_cmdb_object_type(IPAddress, "cmdb_ci_ip_network")
            >>> ip_to_insert = IPAddress.objects.create()
            >>> does_cmdb_object_exist(ip_to_insert)
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
        Update a CMDBObject. This will update the object with current values of the Django model object.

        Args:
            model_object: Any Django object.

        Raises:
              ValueError: When the CMDBObject for the model_object does not exist.
              AttributeError: Occurs when a field does not contain a mapping field or function.

        Returns:
            CMDBObject that was created.
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
            raise ValueError("You must create a cmdb_object first.")

        # Check the associated fields to the object
        object_fields = cmdb_object.fields

        for field in object_fields:
            if field.model_field:
                # Create value object for the field where the field is the ServiceNow field
                # model_field is the field associated the the ServiceNow field
                self.update_cmdb_object_value(cmdb_object, field, getattr(model_object, field.model_field))
            elif field.model_function:
                # Pass a function instead when the relationship is not directly 1:1
                func = getattr(store, field.model_function)
                if func is not None:
                    self.update_cmdb_object_value(cmdb_object, field, func(model_object))
                else:
                    # Change to console log
                    print("Model Function is incorrect")
            else:
                raise AttributeError("The field {} does not a contain a model_field or model function".format(field))

        cmdb_object.put(self.token.access_token)
        return cmdb_object

    def delete_cmdb_object(self, model_object):
        """
        Delete a CMDBObject. This will delete the mapping between the model object and the SN object. You will need to
        recreate another SN object if the mapping is deleted.

        Args:
            model_object: Any Django object.

        Returns:
            CMDBObject that was deleted.

        Note: This implementation retires the SN Object because of SN permission restrictions. To modify this update the delete method of the cmdb object.
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
            raise ValueError("You must create a cmdb_object first.")

        # Check the associated fields to the object
        object_fields = cmdb_object.fields

        for field in object_fields:
            if field.model_field:
                # Create value object for the field where the field is the ServiceNow field
                # model_field is the field associated the the ServiceNow field
                self.update_cmdb_object_value(cmdb_object, field, getattr(model_object, field.model_field))
            elif field.model_function:
                # Pass a function instead when the relationship is not directly 1:1
                func = getattr(store, field.model_function)
                if func is not None:
                    self.update_cmdb_object_value(cmdb_object, field, func(model_object))
                else:
                    # Change to console log
                    print("Model Function is incorrect")
            else:
                raise AttributeError("The field {} does not a contain a model_field or model function".format(field))

        cmdb_object.delete(self.token.access_token)
        return cmdb_object

    @staticmethod
    def is_cmdb_type_mapped(model_object):
        """
        Determines if a mapping exists for a CMDBObjectType and a model object.

        Args:
            model_object: Any Django object.

        Returns:
            bool: True if it exists, False otherwise.
        """

        model = ContentType.objects.get_for_model(model_object)

        cmdb_object_type_exists = CMDBObjectType.objects.filter(
            content_type=model.id,
        ).exists()

        if cmdb_object_type_exists:
            return True
        return False
