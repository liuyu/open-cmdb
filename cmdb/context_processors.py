#!/usr/bin/env python
# encoding:utf8

from django.conf import settings
from cmdb_menu import CMDB_TOP_MENU
import base_admin

def menu(request):
    return {
        'cmdb_menu': CMDB_TOP_MENU,
        'cmdb_name': settings.CMDB_NAME,
        'cmdb_verison': settings.CMDB_VERSION,
        'base_admin': base_admin.BASE_ADMIN
    }
