from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RoleManagementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'role_managements'
    verbose_name = _('Role Management')