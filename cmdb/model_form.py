#!/usr/bin/env python
# encoding:utf8

from django.forms import ModelForm
from models import *
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.hashers import make_password


class Server_Group_CheckForm(ModelForm):
    class Meta:
        model = Server_Group
        fields = '__all__'


class IDC_CheckForm(ModelForm):
    class Meta:
        model = IDC
        fields = '__all__'


class Project_CheckForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class Server_Role_CheckForm(ModelForm):
    class Meta:
        model = Server_Role
        fields = '__all__'


class Server_Device_CheckForm(ModelForm):
    class Meta:
        model = Server_Device
        fields = '__all__'



class User_CheckFrom(ModelForm):
    class Meta:
        model = User
        fields = ['username',
                  'password',
                  'email',
                  'is_superuser',
                  'is_active',
                  'is_staff',
                  'user_permissions']

    def save(self):
        # 如果密码不是以pbkdf加密字符串开头的, 表示用户输入了自己的密码, 需要重新加密
        if not self.instance.password.startswith("pbkdf2_sha256$"):
            print self.instance.password
            self.instance.password = make_password(self.instance.password)
        super(User_CheckFrom, self).save()

class Group_CheckFrom(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

class Permission_CheckFrom(ModelForm):
    class Meta:
        model = Permission
        fields = '__all__'
