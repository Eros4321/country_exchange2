from django.urls import path
from . import views

urlpatterns = [
    path("countries/refresh", views.refresh_countries, name="countries-refresh"),
    path("countries/", views.list_countries, name="countries-list"),
    path("countries/image", views.serve_image, name="countries-image"),
    path("status", views.status_view, name="status"),
    path("countries/<str:name>", views.country_detail, name="countries-detail"),
]
