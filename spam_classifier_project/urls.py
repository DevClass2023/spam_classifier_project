from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('core/', include('core.urls')),
    path('api/ml/', include('ml_service.urls')), # API endpoint for ML service
    # Redirect root to login page.
    path('', RedirectView.as_view(url='core/login/', permanent=False)),
]