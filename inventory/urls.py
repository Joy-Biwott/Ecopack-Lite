# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Bags
    path('bags/', views.bag_list, name='bag_list'),
    path('bags/add/', views.bag_create, name='bag_create'),
    path('bags/update/<int:pk>/', views.bag_update, name='bag_update'),
    path('bags/delete/<int:pk>/', views.bag_delete, name='bag_delete'),

    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_create, name='client_create'),
    path('clients/update/<int:pk>/', views.client_update, name='client_update'),
    path('clients/delete/<int:pk>/', views.client_delete, name='client_delete'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_create, name='order_create'),

    # Feedback (Dev Log)
    path('feedback/', views.feedback_create, name='feedback_create'),
    path('dev/issues/', views.feedback_list, name='feedback_list'),  # <--- New

    # Users (Admin Only) - This fixes your error!
    path('users/', views.user_list, name='user_list'),  # <--- New
]