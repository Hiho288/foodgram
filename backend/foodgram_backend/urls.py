from django.contrib import admin
from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView
from django.conf import settings
from django.conf.urls.static import static
# from api.v1.views import CustomTokenCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.v1.urls')),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)