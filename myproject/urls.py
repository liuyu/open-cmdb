# encoding:utf8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
import myproject.api

urlpatterns = patterns('',
                       url(r'^$', lambda x: HttpResponseRedirect('/login/')),
                       url(r'^logout/$', 'cmdb.views.logout_view', name='cmdb_logout'),
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'},
                           name='cmdb_login'),
                       url(r'^home/$', 'cmdb.views.home', name='home'),

                       # 主机管理
                       url(r'cmdb/(?P<model>\w+)/show/$', 'cmdb.views.show_all'),
                       url(r'cmdb/(?P<model>\w+)/delete/(?P<id>\d+)/$', 'cmdb.views.delete'),
                       url(r'cmdb/(?P<model>\w+)/add/(?P<id>\d+)/$', 'cmdb.views.add_modify'),
                       url(r'cmdb/(?P<model>\w+)/modify/(?P<id>\d+)/$', 'cmdb.views.add_modify'),
                       url(r'cmdb/(?P<model>\w+)/import/$', 'cmdb.views.import_data'),

                       # 操作历史
                       url(r'^cmdb/changelog/', include('echelon.urls')),
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns += patterns(
    '',
    url(r'^api/', include(myproject.api.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)
