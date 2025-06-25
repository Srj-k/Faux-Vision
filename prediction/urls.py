from django.urls import path
from .views import predict_view,predict_result_view,predict_from_history

urlpatterns = [
    path("",predict_view, name="predict"),
    path('result/<int:detection_id>/', predict_result_view, name='predict_result'),
    path('predict/history/<int:record_id>/', predict_from_history, name='predict_from_history'),
]
