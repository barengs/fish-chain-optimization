from django.urls import path
from . import views

app_name = 'ships'

urlpatterns = [
    path('', views.ShipListView.as_view(), name='ship_list'),
    path('<int:pk>/', views.ShipDetailView.as_view(), name='ship_detail'),
    path('create/', views.ShipCreateView.as_view(), name='ship_create'),
    path('<int:pk>/update/', views.ShipUpdateView.as_view(), name='ship_update'),
    path('<int:pk>/delete/', views.ShipDeleteView.as_view(), name='ship_delete'),
    path('import/', views.ShipImportView.as_view(), name='ship_import'),
]