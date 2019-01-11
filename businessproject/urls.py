"""businessproject URL Configuration

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
from django.urls import path
from django.conf.urls import url, include
from cebula import views as cebula_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^cebula/',include('cebula.urls',namespace='cebula')),
    path('api/', include('api.urls', namespace='api')),
    url(r'^accounts/login', cebula_views.LogIn.as_view(), name='login'),
    path('accounts/logout', cebula_views.LogOut, name='logout'),
    url(r'^accounts/signup/$',cebula_views.CreateUserView.as_view(),name='signup'),
    url(r'^accounts/signup/done$',cebula_views.RegisteredView.as_view(),name='create_user_done'),
    # path('accounts/', include('allauth.urls')),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

