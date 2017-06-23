"""Parser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from mainapp.views import *

urlpatterns = [
    url(r'^$', main, name='main'),
    url(r'^archive/$', archive, name='archive'),
    url(r'^addcomment/$', add_comment, name='add_comment'),
    url(r'^archivate/$', archivate, name='archivate'),
    url(r'^dearchivate/$', dearchivate, name='dearchivate'),
    url(r'^users/(\w+)$', users, name='users')
]
