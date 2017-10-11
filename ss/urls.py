from django.conf.urls import url
from . import views

app_name = 'ss'

urlpatterns = [

    # /
    url(r'^$', views.index, name='index'),

    url(r'^global_intelligence/g_s/answer/$', views.g_s_answer, name='g_s_index'),

    url(r'^global_intelligence/g_s/ask/$', views.g_s_ask, name='g_s_ask'),

    url(r'^register/$', views.register, name='register'),

    url(r'^login_user/$', views.login_user, name='login_user'),

    url(r'^logout_user/$', views.logout_user, name='logout_user'),

    url(r'^global_intelligence/g_s/account/$', views.g_s_account, name='g_s_account'),

    url(r'^global_intelligence/g_s/my_vote/$', views.g_s_my_vote, name='g_s_my_vote'),
    
    url(r'^global_intelligence/g_s/answer/ratio/(?P<pk>[0-9]+)/$', views.g_s_ratio, name='g_s_ratio'),

    # url(r'^global_intelligence/g_s/history/$', views.g_s_history, name='g_s_history'),
]
