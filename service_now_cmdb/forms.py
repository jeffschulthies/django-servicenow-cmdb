from django import forms

from .models import CMDBObjectValue, CMDBObject, CMDBObjectField, CMDBObjectType

from .models import ServiceNowToken


class CMDBObjectTypeForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectType
        fields = ['name', 'endpoint', 'content_type']


class CMDBObjectFieldForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectField
        fields = ['name', 'model_field', 'model_function', 'type', 'order']


class CMDBObjectForm(forms.ModelForm):
    class Meta:
        model = CMDBObject
        fields = ['type', 'service_now_id']


class CMDBObjectValueForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectValue
        fields = ['object', 'field', 'value']


class ServiceNowTokenForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ServiceNowTokenForm, self).__init__(*args, **kwargs)

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        data = ServiceNowToken.get_credentials(username, password)
        token = ServiceNowToken.create_token(data, self.user)
        return True
