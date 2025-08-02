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
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # Основни
    path("", include("news.urls")),
    path("admin/", admin.site.urls),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path(
        "home/", include("common.urls")
    ),  # начална страница след login

    # Основна функционалност (всичко изисква login)
    path("clients/", include("clients.urls", namespace="clients")),
    path("contracts/", include("contracts.urls", namespace="contracts")),
    path(
        "loan_requests/",
        include(("loan_requests.urls", "requests"), namespace="requests"),
    ),
    path("annexes/", include("annexes.urls", namespace="annexes")),
    path("reports/", include("reports.urls", namespace="reports")),
    path("nomenclatures/", include("nomenclatures.urls", namespace="nomenclatures")),
    path("logs/", include("logs.urls", namespace="logs")),
    path("api/", include("api.urls", namespace="api")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# За media файлове – development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # За production (Azure Web App)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
