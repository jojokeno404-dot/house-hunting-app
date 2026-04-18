from django.urls import path
from . import views

urlpatterns = [
    path('', views.apartment_list, name='apartment_list'),

    # Apartment Detail - This was missing
    path('apartment/<int:apartment_id>/', views.apartment_detail, name='apartment_detail'),

    # Payment Routes
    path('pay/<int:apartment_id>/', views.pay_for_agent_details, name='pay_for_agent_details'),
    path('initiate-payment/<int:apartment_id>/', views.initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('payment/processing/<int:apartment_id>/', views.payment_processing, name='payment_processing'),
    path('agent-details/<int:apartment_id>/', views.show_agent_details, name='show_agent_details'),
    path('add-apartment/', views.add_apartment, name='add_apartment'),
    # M-Pesa Callback
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
]