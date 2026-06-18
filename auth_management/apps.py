from django.apps import AppConfig


class AuthManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_management'

    def ready(self):
        from django.contrib import admin
        from rest_framework.authtoken.models import Token

        try:
            admin.site.unregister(Token)
        except admin.sites.NotRegistered:
            pass
