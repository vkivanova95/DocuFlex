"""
URL configuration for DocuFlex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('news.urls')),
    path('admin/', admin.site.urls),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('home/', include('common.urls')),  # начална страница за работа в DocuFlex след login

    # Останалите аппове (изискват login)
    path('clients/', include('clients.urls', namespace='clients')),
    # path('', include('common.urls')),
    path('contracts/', include('contracts.urls', namespace='contracts')),
    path('loan_requests/', include(('loan_requests.urls', 'requests'), namespace='requests')),
    path('annexes/', include('annexes.urls', namespace='annexes')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('nomenclatures/', include('nomenclatures.urls', namespace='nomenclatures')),
    path('logs/', include('logs.urls', namespace='logs')),
    path('api/', include('api.urls', namespace='api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
