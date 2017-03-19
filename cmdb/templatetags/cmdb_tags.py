#!/usr/bin/env python
#encoding:utf8
from django import template
import re

register = template.Library()

@register.simple_tag
def menu_active(request, pattern):
    if re.search(r'^'+pattern, request.path):
        return 'active'
    return ''


@register.simple_tag
def get_field_name(table_field, key, attr):
    if not attr:
        attr = 'verbose_name'
    if table_field.get(key, ''):
        return table_field[key][attr]
    return ''


@register.simple_tag
def get_field_value(one_data, field, attr):
    if one_data.get(field, ''):
        return one_data[field][attr]
    return ''


@register.filter('getitem')
def getitem(item, string):
    try:
        return item.get(string, '')
    except :
        return ''


@register.filter("tostring")
def tostring(value):
    try:
        return str(value)
    except:
        return ''
