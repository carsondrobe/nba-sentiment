from django.urls import path
from .views import home, analyze_sentiment, rankings, about

urlpatterns = [
    path("", home, name="home"),
    path("analyze-sentiment/", analyze_sentiment, name="analyze_sentiment"),
    path("rankings/", rankings, name="rankings"),
    path("about/", about, name="about"),
]
