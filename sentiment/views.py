from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import players


def analyze_sentiment(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(text)

        return render(
            request,
            "sentiment/sentiment_analysis.html",  # Adjust the path based on your template structure
            {"text": text, "sentiment_scores": sentiment_scores},
        )

    return render(
        request, "sentiment/sentiment_analysis.html"
    )  # Adjust the path based on your template structure


def home(request):
    text = request.POST.get("text", "")
    player_results = []

    if request.method == "POST" and text:
        # Find players by full name using nba_api
        player_results = players.find_players_by_full_name(text)

    return render(
        request, "sentiment/home.html", {"text": text, "player_results": player_results}
    )
