# coding:utf-8
from django.conf.urls import url
from meet import views

app_name = 'meet'

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^reg/$', views.reg, name="reg"),
    url(r'^$', views.index),
    url(r'^booking/$', views.booking),
    url(r'^log_out/$', views.log_out, name='log_out'),
    url(r'^addevice/$', views.addevice),
    # url(r'^searchdevice/$', views.searchdevice, name='searchdevice'),
]
