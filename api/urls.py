"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework import routers
from api.views.song import SongViewSet
from api.views.songstat import SongStatViewSet


def register_routes():
    routes_to_be_registred = [
        {
            'base_name':    r'songs',
            'ModelViewSet': SongViewSet
        },
        {
            'base_name': r'songstats',
            'ModelViewSet': SongStatViewSet
        }
    ]

    for path in routes_to_be_registred:
        router.register(prefix=path['base_name'], viewset=path['ModelViewSet'], base_name=path['base_name'])


router = routers.DefaultRouter()
register_routes()

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]