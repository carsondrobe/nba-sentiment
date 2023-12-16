from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer


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
