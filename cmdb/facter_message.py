#!/usr/bin/env python
# encoding: utf8
__authors__ = ['liuyu', 'chenlijun']
__version__ = 1.0
__date__ = '2015-09-06 14:58:23'
__licence__ = 'GPL licence'

# 导入模块
import yaml
import os
# 使用IPy主要用来判断ip类型，IPy.IP('ip').iptype()
import IPy

# yaml文件目录
yaml_dir = '/var/lib/puppet/yaml/facts'

# 结果集,结果集的格式{'cmdb_agent':()}
all_host_facter_message = {}

# 结果列表
result_list = ['name',
               'sn',
               'public_ip',
               'private_ip',
               'mac',
               'os',
               'disk',
               'mem',
               'cpu',
               'idc',
               'role',
               'status',
               'admin',
               'memo']

# db对应的facter字段,需要取其他的字段可以一一对应
list_field = {'name': 'fqdn',
              'public_ip': 'ipaddress__interfaces',
              'private_ip': 'ipaddress__interfaces',
              'mac': 'macaddress__interfaces',
              'os': ['operatingsystem', 'operatingsystemrelease', 'hardwaremodel'],
              'disk': 'blockdevice__blockdevices',
              'mem': 'memorysize',
              'cpu': ['processorcount', 'processor0']}

# ruby objectobjectconstruct
def construct_ruby_object(loader, suffix, node):
    return loader.construct_yaml_map(node)


def construct_ruby_sym(loader, node):
    return loader.construct_yaml_str(node)


# 读取数据
def yaml_file_handle(filename):
    stream = open(filename)
    mydata = yaml.load(stream)
    return mydata


# 取ip得类型
def get_ip_type(ip):
    try:
        return IPy.IP(ip).iptype().lower()
    except Exception, e:
        print e


# 处理单个agent的数据
def handle_facter_message(data):
    # 定义一个结果字典，字段和db一样，处理完的结果和db中的一样
    result_dict = {}
    # 对结果进行处理
    for db_field in result_list:
        # 定义一个字段结果字符
        value = ''
        # result_list中的字段是否在我们需要的facter取值列表中，如果存在
        if db_field in list_field:
            facter_field = list_field[db_field]
            # 判断facter_field类型，然后进行处理
            if type(facter_field) == type([]):
                for tag in facter_field:
                    if data.get(tag):
                        value += data[tag] + ' '
            else:
                # 由于disk、ip等需要进一步处理，所以用了一个__来分割，然后处理
                field_tmp = facter_field.split("__")
                if len(field_tmp) == 2:
                    if db_field == 'disk':
                        for tag in data[field_tmp[1]].split(","):
                            # 对磁盘进行处理, 由于磁盘的字段为blockdevice_type_size，所有需要单独处理
                            f = field_tmp[0] + '_' + tag + '_' + 'size'
                            if data.get(f):
                                # 去除sr0 tag的字段
                                if tag != 'sr0':
                                    # 结果字符串
                                    value += tag + ':' + str(int(data[f]) / 1024 / 1024 / 1024) + 'G' + ' '
                    # 对外网ip进行处理
                    elif db_field == 'public_ip':
                        for tag in data[field_tmp[1]].split(","):
                            f = field_tmp[0] + '_' + tag
                            if data.get(f):
                                # 去除lo tag的字段
                                if tag != 'lo':
                                    if get_ip_type(data[f]) == 'public':
                                        # 结果字符串
                                        value += tag + ':' +data[f] + ' '
                    # 对内外ip进行处理
                    elif db_field == 'private_ip':
                        for tag in data[field_tmp[1]].split(","):
                            f = field_tmp[0] + '_' + tag
                            if data.get(f):
                                # 去除lo tag的字段
                                if tag != 'lo':
                                    if get_ip_type(data[f]) == 'private':
                                        # 结果字符串
                                        value += tag + ':' +data[f] + ' '
                    else:
                        # 其他的字段就直接处理了
                        for tag in data[field_tmp[1]].split(","):
                            f = field_tmp[0] + '_' + tag
                            if data.get(f):
                                # 去除lo tag的字段
                                if tag != 'lo':
                                    # 结果字符串
                                    value += tag + ':' + data[f] + ' '
                else:
                    if data.get(facter_field):
                        # 结果字符串
                        value = data[facter_field]
            # 结果添加到result列表中
            result_dict[db_field] = value.strip()
        # 如果不存在
        else:
            result_dict[db_field] = ''
    # return 结果字典
    return result_dict


# 定义取facter得函数
def get_all_host_facter_message():
    # 由于puppet的yaml文件是ruby格式的，需要进行转换
    yaml.add_multi_constructor(u"!ruby/object:", construct_ruby_object)
    yaml.add_constructor(u"!ruby/sym", construct_ruby_sym)
    # 获取所有有facters信息的主机文件名称
    for dirpath, dirnames, filenames in os.walk(yaml_dir):
        # 只需要处理yaml目录下得yaml结尾的文件
        if dirpath == yaml_dir:
            for file in filenames:
                file_name, file_ext = os.path.splitext(file)
                if file_ext == '.yaml':
                    host_yaml_path = yaml_dir + '/' + file
                    # 得到yaml文件内容, 字典形式
                    host_yaml_result_dict = yaml_file_handle(host_yaml_path)
                    # 对单个agent的数据进行处理
                    if host_yaml_result_dict:
                        # 有key为facts,所以可以直接查找facts key值
                        if host_yaml_result_dict.has_key('facts'):
                            data_dict = host_yaml_result_dict['facts']['values']
                        # 没有的直接取
                        else:
                            data_dict = host_yaml_result_dict['values']

                    # 现在就可以data数据进行处理，取得我们所需要得数据
                    result_dict = handle_facter_message(data_dict)
                    all_host_facter_message[file_name] = result_dict
    # return我们最终的数据结果集
    return all_host_facter_message