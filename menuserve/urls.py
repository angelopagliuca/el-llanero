from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('bag/', views.bag, name="bag"),
    path('bag/ajax/change-quantity/', views.change_quantity, name='change_quantity'),
    path('menu/', views.menu, name="menu"),
    path('edit-menu/', views.edit_menu, name="edit-menu"),
    path('orders/', views.orders, name="orders"),
    path('orders/ajax/refresh-orders-ajax/', views.refresh_orders_ajax, name='refresh_orders_ajax'),
    path('orders/refresh-orders/', views.refresh_orders, name='refresh_orders'),
    path('locations/', views.locations, name="locations"),
    path('portal/', views.portal, name="portal"),
    path('portal/<int:id>/', views.add_location_to_employee, name="add_loc_employee"),
    path('sign-in/', views.sign_in, name="sign-in"),
    path('logout/', views.logout_view, name="logout"),
]
