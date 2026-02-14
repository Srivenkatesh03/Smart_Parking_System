from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('setup/', views.setup_view, name='setup'),
    path('logs/', views.logs_view, name='logs'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('allocation/', views.allocation_view, name='allocation'),
    path('references/', views.references_view, name='references'),
    
    # API endpoints
    path('api/save-spaces/', views.SaveParkingSpacesView.as_view(), name='api_save_spaces'),
    path('api/load-spaces/', views.LoadParkingSpacesView.as_view(), name='api_load_spaces'),
    path('api/status/', views.ParkingStatusAPI.as_view(), name='api_status'),
]
