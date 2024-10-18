from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('fetch-orders/', views.fetch_orders, name='fetch_orders'), 
    path('submit-order/', views.submit_order, name='submit_order'),
    path('order_system/', views.order_system, name='order_system'),
    path('chef/', views.chef_view, name='chef_page'),
    
    
]
