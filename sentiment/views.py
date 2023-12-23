from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import teams
from dotenv import load_dotenv
import os


def analyze_sentiment(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        selected_team = request.POST.get("selected_team", "")
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(text)

        return render(
            request,
            "sentiment/sentiment_analysis.html",  # Adjust the path based on your template structure
            {
                "selected_team": selected_team,
                "text": text,
                "sentiment_scores": sentiment_scores,
            },
        )

    return render(
        request, "sentiment/sentiment_analysis.html"
    )  # Adjust the path based on your template structure


def home(request):
    text = request.POST.get("teams_name", "")
    teams_results = []

    if request.method == "POST" and text:
        # Find players by full name using nba_api
        teams_results = teams.find_teams_by_full_name(text)

    return render(
        request, "sentiment/home.html", {"text": text, "teams_results": teams_results}
    )


# Run this whenever you need to use the API Key configure()


# Then use os.getenv('api_key_name')
def configure():
    load_dotenv()
