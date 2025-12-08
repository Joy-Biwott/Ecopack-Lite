from django.contrib import admin
from django.urls import path, include

from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/register/', inventory_views.register, name='register'),
    path('', include('inventory.urls')),

]
