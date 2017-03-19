#!/usr/bin/env python
# encoding:utf8

from models import *
from model_form import *
from django.contrib.auth.models import User, Permission

# 定义模板
BASE_ADMIN = {
    'server_device': {
        'model': Server_Device,
        'form': Server_Device_CheckForm,
        'name': u'主机',
        'import': 'open',
        'list_display': ['name',
                         'sn',
                         'public_ip',
                         'private_ip',
                         'mac',
                         'os',
                         'disk',
                         'cpu',
                         'idc',
                         'role',
                         'status',
                         'admin',
                         'memo'],
        'readonly': ['name'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/server_device/modify/'),]
    },

    'idc': {
        'model': IDC,
        'form': IDC_CheckForm,
        'name': u'IDC',
        'import': '',
        'list_display': ['name',
                         'memo'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/idc/modify/'),]
    },

    'project': {
        'model': Project,
        'form': Project_CheckForm,
        'name': u'项目',
        'import': '',
        'list_display': ['name',
                         'memo'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/project/modify/'),]
    },

    'server_group': {
        'model': Server_Group,
        'form': Server_Group_CheckForm,
        'name': u'项目组',
        'import': '',
        'list_display': ['name',
                         'project',
                         'memo'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/server_group/modify/'),]
    },

    'server_role': {
        'model': Server_Role,
        'form': Server_Role_CheckForm,
        'name': u'主机角色',
        'import': '',
        'list_display': ['name',
                         'group',
                         'memo'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/server_role/modify/'),]
    },

    'user': {
        # model名称
        'model': User,
        # form表单
        'form': User_CheckFrom,
        # 名称
        'name': u'用户管理',
        # 是否可以导入信息
        'import': '',
        # table展示字段
        'list_display': ['username',
                         'password',
                         'email',
                         'is_superuser',
                         'is_active',
                         'is_staff',
                         'groups',
                         'user_permissions'],
        # 编辑的时候只读字段
        'readonly': ['username', ], #'password'
        # 动作
        'action_list': [(u'编辑', 'pencil', '/cmdb/user/modify/'),]
    },

    'group': {
        # model名称
        'model': Group,
        # form表单
        'form': Group_CheckFrom,
        # 名称
        'name': u'用户组管理',
        # 是否可以导入信息
        'import': '',
        # table展示字段
        'list_display': ['name',
                         'permissions'],
        # 编辑的时候只读字段
        'readonly': ['name', ],
        # 动作
        'action_list': [(u'编辑', 'pencil', '/cmdb/group/modify/'),]
    },

    'permission': {
        'model': Permission,
        'form': Project_CheckForm,
        'name': u'权限管理',
        'import': '',
        'list_display': ['name',
                         'content_type',
                         'codename'],
        'action_list': [(u'编辑', 'pencil', '/cmdb/permission/modify/'),]
    }


}
