from django.contrib import admin
from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView
# from api.v1.views import CustomTokenCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('api.v1.urls')),
    
    # path('admin/', admin.site.urls),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    # path('api/', include('users.urls')),
    
]
