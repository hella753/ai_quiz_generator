"""
URL configuration for ai_quiz_generator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="AI Quiz Generator API",
        default_version='v1',
        description="""
        Backend API built with Django, for AI Quiz Generator. 
        Provides endpoints to handle Quiz Generating, 
        Quiz Correcting and Authorization. 
        Excellent Tool for Teachers and Students to 
        Develop their skills and make studying easier.
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="interpredators.django@gmail.com"),
        license=openapi.License(name='''Copyright (c) 2024 Interpredators /
                                    Created by: Interpredators /
                                    Date: November 25, 2024'''),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [

    path('accounts/', include('user.urls', namespace="user")),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/', include('quiz_app.urls', namespace="quiz_app")),
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

