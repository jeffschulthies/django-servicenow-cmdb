from django.apps import AppConfig


class ServiceNowCMDB(AppConfig):
    name = 'service-now-cmdb'
    verbose_name = 'ServiceNowCMDB'

    def ready(self):
        pass
