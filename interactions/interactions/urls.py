from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('staff/', include('staff.urls')),
    path('manager/', include('managers.urls')),
    path('worker/', include('workers.urls')),
]
