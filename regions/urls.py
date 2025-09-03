from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    path('', views.FishingAreaListView.as_view(), name='fishing_area_list'),
    path('<int:pk>/', views.FishingAreaDetailView.as_view(), name='fishing_area_detail'),
    path('create/', views.FishingAreaCreateView.as_view(), name='fishing_area_create'),
    path('<int:pk>/update/', views.FishingAreaUpdateView.as_view(), name='fishing_area_update'),
    path('<int:pk>/delete/', views.FishingAreaDeleteView.as_view(), name='fishing_area_delete'),
    path('template/', views.FishingAreaTemplateDownloadView.as_view(), name='fishing_area_template_download'),
]