from django.urls import path
from .views import home, analyze_sentiment, rankings

urlpatterns = [
    path("", home, name="home"),
    path("analyze-sentiment/", analyze_sentiment, name="analyze_sentiment"),
    path("rankings/", rankings, name="rankings"),
]
