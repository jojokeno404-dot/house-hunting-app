from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import only existing views
from properties.views import (
    apartment_list,
    pay_for_agent_details,
    initiate_mpesa_payment,
    payment_processing,
    show_agent_details,
    mpesa_callback,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include app URLs
    path('', include('properties.urls')),

    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)