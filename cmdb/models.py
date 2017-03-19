# !/usr/bin/env python
# encoding:utf8
# 从django.db中导入models模块
from django.db import models
# 导入User模块
from django.contrib.auth.models import User
# Create your models here.
# 定义一个Server_Group类，从models.Model中继承，这里也就是所谓得数据表结构
class Server_Group(models.Model):
    # 定义主机组名称字段
    name = models.CharField(u'主机组', max_length=255, unique=True)
    # 关联的项目字段，这是关联一个外键
    project = models.ForeignKey("Project", verbose_name='项目名称')
    # 备注字段
    memo = models.CharField(u'备注', max_length=255, blank=True)
    # unicode返回值
    def __unicode__(self):
        # 返回的格式
        return '%s-%s' % (self.project.name, self.name)

    # 定义Meta属性
    class Meta:
        # 数据库中的表名
        db_table = 'server_group'
        # 存储的时候确认组合键唯一
        unique_together = (("name", "project"),)


# 定义一个IDC类，主要存储IDC信息，数据表结构有2个字段
class IDC(models.Model):
    # 定义IDC的名称字段
    name = models.CharField(u'IDC名称', max_length=255, unique=True)
    memo = models.CharField(u'备注', max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'idc'


# 定义一个Project类，主要存储项目信息，数据表结构有2个字段
class Project(models.Model):
    name = models.CharField(u'项目名称', max_length=255, unique=True)
    memo = models.CharField(u'备注', max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'project'


# 定义一个Server_Role类，主要存储服务器角色信息，数据表结构有3个字段
class Server_Role(models.Model):
    name = models.CharField(u'角色', max_length=255)
    # 关联Server_Group，也就是服务器组
    group = models.ForeignKey("Server_Group", verbose_name='项目组')
    memo = models.CharField(u'备注', max_length=255, blank=True)

    def __unicode__(self):
        return '%s-%s-%s' % (self.group.project.name, self.group.name, self.name)

    class Meta:
        # 设置数据库表名
        db_table = 'server_role'
        # 存储的时候确认组合键唯一
        unique_together = (("name", "group"),)


# CMDB核心数据表结构，用来存在服务器系统信息
class Server_Device(models.Model):
    # 服务器状态选择，具体的字段存储数据为0-3的int数字
    SERVER_STATUS = (
        (0, u'下线'),
        (1, u'在线'),
        (2, u'待上线'),
        (3, u'测试'),
    )
    # 定义一个名称字段,blank没有设置默认为False不能为空，且unique=True必须唯一
    name = models.CharField(u'主机名称', max_length=100, unique=True)
    # 定义SN编号字段， blank=True可以为空
    sn = models.CharField(u'SN号', max_length=200, blank=True)
    # 公网IP字段，可以为空
    public_ip = models.CharField(u'外网IP', max_length=200, blank=True)
    # 私网IP，可以为空
    private_ip = models.CharField(u'内网IP', max_length=200, blank=True)
    # 定义mac地址字段
    mac = models.CharField(u'MAC地址', max_length=200, blank=True)
    # 定义操作系统字段
    os = models.CharField(u'操作系统', max_length=200, blank=True)
    # 定义磁盘信息字段
    disk = models.CharField(u'磁盘', max_length=200, blank=True)
    # 定义内存信息字段
    mem = models.CharField(u'内存', max_length=200, blank=True)
    # 定义CPU信息字段
    cpu = models.CharField(u'CPU', max_length=200, blank=True)
    # 关联IDC信息
    idc = models.ForeignKey(IDC, max_length=255, blank=True, null=True, verbose_name='机房名称')
    # 定义个多对多字段，一台服务器可以对应多一个角色
    role = models.ManyToManyField("Server_Role", verbose_name='角色', blank=True)
    # 机器状态，默认都为在线状态
    status = models.SmallIntegerField(verbose_name='机器状态', choices=SERVER_STATUS, default=1)
    # 管理用户信息
    admin = models.ForeignKey('auth.User', verbose_name='管理员', null=True, blank=True)
    # 定义备注字段
    memo = models.CharField(u'备注', max_length=200, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'server_device'
