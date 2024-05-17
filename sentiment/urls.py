from django.urls import path
from .views import home, analyze_sentiment, rankings, about, team_detail
from . import views

urlpatterns = [
    path("", home, name="home"),
    path("analyze-sentiment/", analyze_sentiment, name="analyze_sentiment"),
    path("rankings/", rankings, name="rankings"),
    path("about/", about, name="about"),
    path("team/<str:team_name>/", team_detail, name="team_detail"),
    path("analysis/", views.analysis, name="analysis"),
]

htmx_urls = [
    path("get_team_data/", views.get_team_data, name="get_team_data"),
]

urlpatterns += htmx_urls
