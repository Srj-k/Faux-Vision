from .views import landing_page
from django.urls import path,include

urlpatterns = [
    path('',landing_page,name='landing')
]