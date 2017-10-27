from django.contrib import admin

from service_now_cmdb.forms import CMDBObjectForm, CMDBObjectTypeForm, CMDBObjectFieldForm, CMDBObjectValueForm
from service_now_cmdb.models import CMDBObjectType, CMDBObjectField, CMDBObject, CMDBObjectValue


@admin.register(CMDBObjectType)
class CMDBObjectTypeAdmin(admin.ModelAdmin):
    form = CMDBObjectTypeForm
    list_display = ['name', 'endpoint', 'content_type']


@admin.register(CMDBObjectField)
class CMDBObjectFieldAdmin(admin.ModelAdmin):
    form = CMDBObjectFieldForm
    list_display = ['name', 'type', 'order']


@admin.register(CMDBObject)
class CMDBObjectAdmin(admin.ModelAdmin):
    form = CMDBObjectForm
    list_display = ['type', 'service_now_id']


@admin.register(CMDBObjectValue)
class CMDBObjectValueAdmin(admin.ModelAdmin):
    form = CMDBObjectValueForm
    list_display = ['object', 'field', 'value']

