"""dogoweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from stats import views as stats_views
from spam import views as spam_views

urlpatterns = [
    url(r'favicon.ico', RedirectView.as_view(url='/static/dogoweb/img/favicon.ico', permanent=True)),
    url(r'^$', RedirectView.as_view(pattern_name='pizarron', permanent=False)),
    url(r'pizarron', stats_views.pizarron, name='index'),
    url(r'config', spam_views.config, name='config'),
    path('seg/', include('seg.urls')),
    path('mail/', include('mail.urls')),
    path('spam/', include('spam.urls')),
    path('erp/', include('erp.urls')),
    path('stats/', include('stats.urls')),
    path('admin/', admin.site.urls),
]# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
