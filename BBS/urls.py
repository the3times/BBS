"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views

from django.views.static import serve
from BBS import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.RegView.as_view(), name='register'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^get_code/', views.get_code, name='get_code'),
    url(r'^index/', views.index, name='index'),
    url(r'^reset_password/', views.reset_password, name='reset_password'),
    url(r'^change/avatar/', views.change_avatar, name='change_avatar'),
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^get_user_avatar/', views.get_user_avatar),

    url(r'^(?P<username>\w+)/$', views.blog, name='blog'),    # 结尾处加/$
    url(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/', views.blog, name='blog'),

    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail, name='article_detail'),

    url(r'^up_and_down/&', views.up_and_down, name='up_and_down'),   # 加一个&是为了避免和个人站点url匹配冲突

    url(r'^article/comment/', views.article_comment, name='article_comment'),

    url(r'^i/backend/', views.backend, name='backend'),
    url(r'^article/add/', views.ArticleAddView.as_view(), name='article_add'),
    url(r'^upload/article_img/', views.upload_img, name='upload_img'),
    url(r'^article/edit/(\d+)/', views.ArticleEditView.as_view(), name='article_edit'),
    url(r'^article/delete/(\d+)/', views.article_delete, name='article_delete'),

]
