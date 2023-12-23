from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import teams
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta


def analyze_sentiment(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        selected_team = request.POST.get("selected_team", "")
        youtube_analysis(selected_team)
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


def youtube_analysis(team_name):
    configure()
    API_KEY = os.getenv("youtube_api_key")

    # Initialize YouTube API
    youtube = build("youtube", "v3", developerKey=API_KEY)

    # Calculate the date 7 days ago
    published_after = (datetime.now() - timedelta(days=7)).isoformat() + "Z"

    # Search for videos with team_name in the title
    search_response = (
        youtube.search()
        .list(
            q=f"{team_name} FULL GAME HIGHLIGHTS highlights full game",
            part="id,snippet",
            type="video",
            maxResults=2,  # Adjust the number of results as needed
            channelId="UCWJ2lWNubArHWmf3FIHbfcQ",  # NBA Official Youtube Channel ID
            publishedAfter=published_after,
        )
        .execute()
    )

    # Extract video information
    videos = search_response.get("items", [])

    # Create a list for video IDs
    video_id_list = []
    # Display video titles and IDs
    for video in videos:
        video_id = video["id"]["videoId"]
        video_id_list.append(video_id)
        video_title = video["snippet"]["title"]
        print(f"Video Title: {video_title}, Video ID: {video_id}")
