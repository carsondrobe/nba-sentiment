from django.urls import path
from .views import home, analyze_sentiment

urlpatterns = [
    path("", home, name="home"),
    path("analyze-sentiment/", analyze_sentiment, name="analyze_sentiment"),
]
