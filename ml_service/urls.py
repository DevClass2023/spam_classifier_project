from django.urls import path
from .views import PredictSpamAPIView

urlpatterns = [
    path('predict/', PredictSpamAPIView.as_view(), name='predict_spam'),
]