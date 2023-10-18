"""resource_provider URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin

from myapp import views


urlpatterns = [
    re_path(r'^$', views.Home.as_view(), name='index'),
    re_path(r'^secured$', views.Secured.as_view(), name='secured'),
    re_path(r'^permission$', views.Permission.as_view(), name='permission'),
    re_path(r'^keycloak/', include('django_keycloak.urls')),
    re_path(r'^admin/', admin.site.urls),
]
