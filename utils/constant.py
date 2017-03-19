# -*- coding: utf-8 -*-

# 字段类型与HTML控件的对应关系; 注意，如果model中有用到到新的类型，此处必须添加对应项
FIELD_WIDGETS = {
    "ForeignKey": "enumerate",
    "OneToOneField": "enumerate",
    "ManyToManyField": "multiselect2",

    "CharField": "input",
    "SlugField": "input",
    "TextField": "textarea",
    "GenericIPAddressField": "input",

    "AutoField": "input",
    "BooleanField": "checkbox",
    "SmallIntegerField": "input",
    "BigIntegerField": "input",
    "DecimalField": "input",
    "EmailField": "input",
    "DateField": "datetime",
    "DateTimeField": "datetime",

}

FOREIGNKEY_FUNCS = ['__foreign_unicode__',
                    '__unicode__']