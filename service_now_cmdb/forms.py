from django import forms

from .models import CMDBObjectValue, CMDBObject, CMDBObjectField, CMDBObjectType


class CMDBObjectTypeForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectType
        fields = ['name', 'endpoint', 'content_type']


class CMDBObjectFieldForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectField
        fields = ['name', 'type', 'order']


class CMDBObjectForm(forms.ModelForm):
    class Meta:
        model = CMDBObject
        fields = ['type', 'service_now_id']


class CMDBObjectValueForm(forms.ModelForm):
    class Meta:
        model = CMDBObjectValue
        fields = ['object', 'field', 'value']
