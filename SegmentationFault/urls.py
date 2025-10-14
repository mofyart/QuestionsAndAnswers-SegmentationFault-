from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('ask/', include('app.urls')),
    path('question/', include('app.urls')),
    path('tag/', include('app.urls')),
    path('settings/', include('app.urls')),
    path('login/', include('app.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
