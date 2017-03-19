#!/usr/bin/env python
# encoding:utf8

import copy
import uuid

from django.db.models import ManyToManyField
from django.db.models import ForeignKey
from django.db.models import BooleanField
from django.db.models import OneToOneField
from django.db.models import NOT_PROVIDED
from django.utils import log

from constant import FIELD_WIDGETS, FOREIGNKEY_FUNCS

logger = log.getLogger('except')
admin_new_model_group_name = {}


def choices_enum_get(choices, value):
    for v, k in choices:
        if value == v:
            return k
    return value


def get_data_from_model(model, obj=None):
    """
    获取model中的字段数据, 并以字典形式返回
    参考了django ModelForm获取model fields的方法
    """
    data_from_obj = {}  # 定义一个结果集

    opts = model._meta  # 取model得Meta属性集合

    for f in opts.fields + opts.many_to_many:
        name = getattr(f, 'name')
        help_text = getattr(f, 'help_text')
        no_blank = not getattr(f, 'blank', False)
        verbose_name = getattr(f, 'verbose_name')
        default = getattr(f, 'default', '')
        if default == NOT_PROVIDED:
            default = ''
        f_val = f_text = default      # 如果取不到value, 则取''
        show_type = 'show_str'

        if type(f) == BooleanField:
            show_type = 'show_bool'

        cdata_block = {
            'field': name,
            'value': f_val,
            'text': f_text,  # 用于表格展示
            'class': '',
            'field_type': type(f),
            'field_widget': FIELD_WIDGETS[type(f).__name__],
            'verbose_name': verbose_name,
            'help_text': help_text,
            'no_blank': no_blank,
            'show_type': show_type,
            'errormsg': ''
        }
        try:
            if obj:
                f_val = f_text = getattr(obj, name)
                if f_val is None:
                    f_val = f_text = ''

            if type(f) in [ForeignKey, OneToOneField]:
                if f_val:
                    for foreign_func in FOREIGNKEY_FUNCS:
                        if hasattr(f_val, foreign_func):
                            _f_data = f_val
                            f_val = getattr(_f_data, 'id')
                            f_text = getattr(_f_data, foreign_func)()
                            break  # 使用第一个可以取到值的外键函数

            elif type(f) == ManyToManyField:
                if not obj:
                    pass
                else:
                    _f_data = {c.id: c.__unicode__() for c in f_val.all()}
                    f_val = _f_data.keys()
                    f_text = ", ".join(_f_data.values())

            choices_enum = getattr(f, 'choices', None)
            if choices_enum:
                f_text = choices_enum_get(choices_enum, f_val)
                cdata_block['field_widget'] = "enumerate"

        except Exception, e:
            logger.exception(u"get_data error: %s" % e)
            f_val = default      # 如果取不到value, 则取''

        if name == 'id':    # id 直接填写
            if f_val == '':
                cdata_block = 0   # 无则改成 0
            else:
                cdata_block = f_val
        else:
            cdata_block['value'] = f_val
            cdata_block['text'] = f_text

        data_from_obj[name] = cdata_block

    data_from_obj['admin_new_fakeid'] = uuid.uuid4()
    data_from_obj['admin_new_inline_status'] = 'normal'

    return data_from_obj


def get_foreignkeys_edit_context(model_name, model_obj=None):
    global G_ADMINNEW_UPDATED_VERSION

    foreignkeys_mchoices_keys = {}

    model_version_need_update = []

    opts = model_name._meta
    for f in opts.fields:
        name = getattr(f, 'name')
        try:
            if hasattr(f, 'choices') and getattr(f, 'choices'):
                foreignkeys_mchoices_keys[name] = getattr(f, 'choices')

            if type(f) in [ForeignKey, OneToOneField]:
                rel_model = f.rel.to

                limit_choices_to = getattr(f.rel, 'limit_choices_to', None)

                # if model_obj and name in self.fields_read_only:
                #     name_obj = getattr(model_obj, name, None)
                #     keynames = [(name_obj.id, name_obj.__unicode__(),
                #                  hasattr(name_obj, '__sort_unicode__') and name_obj.__sort_unicode__() or name_obj.__unicode__()
                #              )]

                if limit_choices_to:
                    Q_results = Q(**limit_choices_to)

                    keynames = [(c.id, c.__unicode__(),
                                 hasattr(c, '__sort_unicode__') and c.__sort_unicode__() or c.__unicode__()
                             ) for c in f.rel.to.objects.filter(Q_results)]
                else:

                    ## Disable Cache
                    ##
                    # if name in self.foreignkeys_mchoices_keys:
                    #     if self.forigenkey_updated_version.get(rel_model, 0) > G_ADMINNEW_UPDATED_VERSION.get(rel_model, 0):
                    #         continue
                    model_version_need_update += [rel_model]

                    Q_queryset = f.rel.to.objects.all()

                    keynames = [(c.id, c.__unicode__(),
                                 hasattr(c, '__sort_unicode__') and c.__sort_unicode__() or c.__unicode__()
                             ) for c in Q_queryset]
                keynames.sort(key=lambda x:x[2])

                # 选择 '-' 表示不关联任何 foreignkey
                can_be_null = getattr(f, 'null', False)
                if can_be_null:
                    keynames = [('', '--请选择--')] + keynames

                foreignkeys_mchoices_keys[name] = keynames
        except Exception, e:
            raise

    return foreignkeys_mchoices_keys


# 编辑时需要的 ManyToMany context
def get_manytomanys_edit_context(model_name, model_obj=None):
    manytomany_keys = {}
    for f in model_name._meta.many_to_many:
        try:
            if type(f) != ManyToManyField:
                continue

            name = getattr(f, 'name')
            queryset = f.rel.to.objects.all()

            mfs = [(c.id, c.__unicode__(),
                    hasattr(c, '__sort_unicode__') and c.__sort_unicode__() or c.__unicode__())
                   for c in queryset]
            mfs.sort(key=lambda x: x[2])
            manytomany_keys[name] = [(cid, cname) for cid, cname, _ in mfs]

        except Exception, e:
            logger.exception(u"get manytomany error: %s" % e)
            raise Exception(e)

    return manytomany_keys

def get_page_choices(page_n, page_max):
    """  计算显示的翻页页码
    Args:
       page_n: 当前页码
       page_max: 最大页码
    return:
       应该显示的页码
    """
    N = 4
    page_max = int(page_max)
    l = max(1, page_n - N)
    r = min(page_max, page_n + N)
    if page_max == 0:
        return [0]

    if page_max > r:
        return [0] + range(l, r) + [page_max - 1]
    return [0] + range(l, r)