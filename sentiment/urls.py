from django.urls import path
from .views import analyze_sentiment

urlpatterns = [
    path("analyze-sentiment/", analyze_sentiment, name="analyze_sentiment"),
]
