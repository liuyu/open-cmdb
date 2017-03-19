# -*- coding: utf-8 -*-
# 导入cmdb.models模块
import cmdb.models
# 从rest_framework中导入模块
from rest_framework import routers, serializers, viewsets

# Server_Group, IDC, Project, Server_Role, Server_Device

# 给需要生成API的model定义一个数据序列
# Serializers define the API representation.
class ServerGroupSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.StringRelatedField()

    class Meta:
        # 使用的model名称
        model = cmdb.models.Server_Group
        # 字段序列
        fields = ('url', 'name', 'project',
                  'memo')


class IDCSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        # 使用的model名称
        model = cmdb.models.IDC
        # 字段序列
        fields = ('url', 'name', 'memo')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = cmdb.models.Project
        # 字段序列
        fields = ('url', 'name', 'memo')


class ServerRoleSerializer(serializers.HyperlinkedModelSerializer):
    group = serializers.StringRelatedField()

    class Meta:
        model = cmdb.models.Server_Role
        # 字段序列
        fields = ('url', 'name', 'group', 'memo')


class ServerDeviceSerializer(serializers.HyperlinkedModelSerializer):
    admin = serializers.StringRelatedField()
    idc = serializers.StringRelatedField()
    role = serializers.StringRelatedField(many=True)

    class Meta:
        model = cmdb.models.Server_Device
        # 字段序列
        fields = ('url', 'name', 'sn', 'public_ip',
                  'private_ip', 'mac', 'os', 'disk', 'mem', 'cpu', 'idc',
                  'role', 'status',
                  'admin', 'memo')


# ViewSets define the view behavior.
class ServerGroupViewSet(viewsets.ModelViewSet):
    queryset = cmdb.models.Server_Group.objects.all()
    serializer_class = ServerGroupSerializer


class IDCViewSet(viewsets.ModelViewSet):
    queryset = cmdb.models.IDC.objects.all()
    serializer_class = IDCSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = cmdb.models.Project.objects.all()
    serializer_class = ProjectSerializer


class ServerRoleViewSet(viewsets.ModelViewSet):
    queryset = cmdb.models.Server_Role.objects.all()
    serializer_class = ServerRoleSerializer


class ServerDeviceViewSet(viewsets.ModelViewSet):
    queryset = cmdb.models.Server_Device.objects.all()
    serializer_class = ServerDeviceSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'server_groups', ServerGroupViewSet)
router.register(r'idcs', IDCViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'server_roles', ServerRoleViewSet)
router.register(r'server_devices', ServerDeviceViewSet)
