# encoding:utf8
# Create your views here.
import json
from math import ceil
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.db.models import Q
from django.db.models import SmallIntegerField, IntegerField, ForeignKey

from base_admin import BASE_ADMIN
from utils.model_utils import get_data_from_model
from utils import model_utils
from facter_message import get_all_host_facter_message
from cmdb_menu import CMDB_TOP_MENU
from django.contrib.auth.models import User
page_size = 15.0

# 登出函数
@login_required
def logout_view(request):
    return logout_then_login(request)


# home页函数
@login_required
def home(request):
    return render_to_response('home.html', locals(), context_instance=RequestContext(request))


# 展示数据函数
# login_require是django自带的一个装饰器函数，主要用来检查当前的用户是否已经登录及其权限
@login_required
def show_all(request, model):
    result = []
    search_content = ''
    # 查看model是否在定义的模板中
    if model in BASE_ADMIN:
        # 获取tag名称
        tag_name = BASE_ADMIN[model]['name']
        # 这个主要是编辑等一些动作
        action_list = BASE_ADMIN[model]['action_list']
        # 获取得展示的字段
        list_display = BASE_ADMIN[model]['list_display']
        # 获取model名称
        model_name = BASE_ADMIN[model]['model']
        # 是否有导入按钮
        import_action = BASE_ADMIN[model]['import']
        # 注意在model的字段注释要写，这样得话，表名的中文字段就可以直接从models中读取
        table_field = get_data_from_model(model_name)

        # 得到数据
        model_data = model_name.objects.all()

        # 得到条数
        total_num = model_data.count()
        # 分页
        page_list = [x + 1 for x in range(int(ceil(total_num / page_size)))]
        last_page = len(page_list)
        # 访问页码
        page = request.GET.get('page', 1)
        page = int(page)
        # 取访问页的区间
        page_zone = model_data[(page - 1) * page_size:page * page_size]
        # 处理数据
        for one_data in page_zone:
            result.append(get_data_from_model(model_name, one_data))
    else:
        # 如果没有跳转到404页面
        return render_to_response('404.html', locals(), context_instance=RequestContext(request))
    # 处理搜索
    if request.method == 'POST':
        kargs = {}
        result = []
        search_content = request.POST.get('search_content', '')
        search_key = request.POST.get('search_key', '')
        # 搜索功能
        if table_field.get(search_key):
            field = table_field[search_key]['field']
            field_type = table_field[search_key]['field_type']

            if field_type in [SmallIntegerField, IntegerField]:
                tmp_search_text = int(search_content)
                kargs[field] = tmp_search_text
            if field_type in [ForeignKey]:
                # print model_name._meta.get_field(field).rel.to
                pass
                # kargs['%s_id' % field] = search_content
            else:
                kargs['%s__icontains' % field] = search_content
            search = Q(**kargs)
            search_data = model_name.objects.filter(search)
            total_num = search_data.count()
            for s_data in search_data:
                result.append(get_data_from_model(model_name, s_data))

    return render_to_response('all_data_show.html', locals(), context_instance=RequestContext(request))  # 删除数据函数


@login_required
def delete(request, model, id):
    id = int(id)
    if model in BASE_ADMIN:
        model_name = BASE_ADMIN[model]['model']
        try:
            # 取得数据
            get_data = model_name.objects.get(id=id)
            # 删除
            get_data.delete()
            # 重定向页面
            return HttpResponseRedirect('/cmdb/%s/show/' % model)
        except Exception, e:
            return e
    else:
        return render_to_response('404.html', locals(), context_instance=RequestContext(request))


@login_required
def add_modify(request, model, id):
    '''输出添加删除的表单，使用modal展示'''
    id = int(id)
    action = ''
    if model not in BASE_ADMIN:
        return render_to_response('404.html', locals(),
                                  context_instance=RequestContext(request))

    # 获取model名称
    model_name = BASE_ADMIN[model]['model']
    # 获取form名称
    form = BASE_ADMIN[model]['form']

    if request.method == 'POST':
        instance = model_name.objects.get(id=id) if id > 0 else None
        form_data = form(request.POST, instance=instance)
        if form_data.is_valid():
            form_data.save()
            return HttpResponse(json.dumps({"result": True}))
        else:
            return HttpResponse(json.dumps({"result": False,
                                            "errors": form_data.errors}))

    return _edit_show(request, model, id)


def _edit_show(request, model, id):
    """渲染一个数据项的页面, 添加或者编辑"""
    # 获取tag名称
    tag_name = BASE_ADMIN[model]['name']
    # 获取model名称
    model_name = BASE_ADMIN[model]['model']
    # 获取得展示的字段
    list_display = BASE_ADMIN[model]['list_display']
    # 获取readyonly字段
    if 'readonly' in BASE_ADMIN[model]:
        readonly_field = BASE_ADMIN[model]['readonly']
    else:
        readonly_field = []
    model_obj = None
    # 所有得添加add id为0
    if id == 0:
        action = 'add'
        tag_name = u'添加' + tag_name
        data = get_data_from_model(model_name)
    else:
        action = 'modify'
        tag_name = u'编辑' + tag_name
        try:
            model_obj = model_name.objects.get(id=id)
            data = get_data_from_model(model_name, model_obj)
        except Exception, e:
            return render_to_response('404.html', locals(),
                                      context_instance=RequestContext(request))

    # 设置foreignkey, 如果get_edit_context中有, 则取出并覆盖初始值:
    mchoices_keys = model_utils.get_foreignkeys_edit_context(model_name, model_obj)

    # 设置manytomany, 如果get_edit_context中有, 则取出并覆盖初始值:
    manytomany_keys = model_utils.get_manytomanys_edit_context(model_name, model_obj)

    return render_to_response('add_modify.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def import_data(request, model):
    # 导入计数器
    import_num = 0
    # 查看model是否在定义的模板中
    if model in BASE_ADMIN:
        # 获取tag名称
        tag_name = BASE_ADMIN[model]['name']
        # 获取model名称
        model_name = BASE_ADMIN[model]['model']
        if model == 'server_device':
            server_device_data = get_all_host_facter_message()
            # 进行数据处理入库
            for hostname, facter_message in server_device_data.items():
                # 主机名处理，判断facter_message中name key有值，
                if facter_message['name']:
                    # name就使用该值
                    name = facter_message['name']
                # 如果没有这个值
                else:
                    # 就使用hostname
                    name = hostname
                # 对于IDC信息、User信息、项目角色信息处理都需要自己去写facter插件，不写都是为空，然后进行处理
                # IDC关联处理，如果facter_message中idc key有值
                if facter_message['idc']:
                    # idc_name就为该值
                    idc_name = facter_message['idc']
                    # 同时处理该IDC信息是否在IDC表中有，如果有取出ID
                    if IDC.objects.filter(name=idc_name):
                        idc_id = IDC.objects.get(name=idc_name).id
                    # 没有,则进行保存，然后取出ID
                    else:
                        idc_sql = IDC(name=idc_name)
                        try:
                            idc_sql.save()
                            # 取出ID
                            idc_id = IDC.objects.get(name=idc_name).id
                        except Exception, e:
                            return e
                # 如果idc key没有值，则为None
                else:
                    idc_id = None
                # 管理员信息关联处理，如果用户存在关联，不存在跳过
                if facter_message['admin']:
                    admin_name = facter_message['admin']
                    # 如果用户存在User表中则取ID，没有为空
                    if User.objects.filter(username=admin_name):
                        user_id = User.objects.get(username=admin_name).id
                    else:
                        user_id = None
                # 没有就为空
                else:
                    user_id = None
                # 这里还有一个角色多对多关系的处理，由于作者这里没有定义机器角色因此在这里不处理角色信息
                # 判断主机是否存在server_device表中，如果不存在添加
                if not model_name.objects.filter(name=name):
                    import_sql = model_name(name=name,
                                            sn=facter_message['sn'],
                                            public_ip=facter_message['public_ip'],
                                            private_ip=facter_message['private_ip'],
                                            mac=facter_message['mac'],
                                            idc=idc_id,
                                            os=facter_message['os'],
                                            disk=facter_message['disk'],
                                            mem=facter_message['mem'],
                                            cpu=facter_message['cpu'],
                                            admin=user_id,
                                            memo=facter_message['memo'],
                    )
                    try:
                        # 保存
                        import_sql.save()
                    except Exception, e:
                        return e
                # 如果有了，查询数据，切信息不对则更新
                elif not model_name.objects.filter(name=name,
                                                   sn=facter_message['sn'],
                                                   public_ip=facter_message['public_ip'],
                                                   private_ip=facter_message['private_ip'],
                                                   mac=facter_message['mac'],
                                                   os=facter_message['os'],
                                                   disk=facter_message['disk'],
                                                   mem=facter_message['mem'],
                                                   cpu=facter_message['cpu'],
                                                   memo=facter_message['memo']):
                    try:
                        # 更新数据库
                        model_name.objects.filter(name=name).update(sn=facter_message['sn'],
                                                                    public_ip=facter_message['public_ip'],
                                                                    private_ip=facter_message['private_ip'],
                                                                    mac=facter_message['mac'],
                                                                    os=facter_message['os'],
                                                                    disk=facter_message['disk'],
                                                                    mem=facter_message['mem'],
                                                                    cpu=facter_message['cpu'],
                                                                    memo=facter_message['memo'],
                        )
                    except Exception, e:
                        return e
                # 如果有了，信息ok，跳过
                else:
                    continue
        return HttpResponseRedirect('/cmdb/%s/show/' % model)

    return render_to_response('all_data_show.html', locals(),
                              context_instance=RequestContext(request))