from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import teams
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from statistics import mean
import spacy
import numpy as np
from .models import NBATeam, TeamSentiment
from django.db import IntegrityError
import schedule
import time

last_update_time = "2024-01-12 14:30:00"


def configure():
    load_dotenv()


def initialize_youtube_api():
    configure()
    API_KEY = os.getenv("youtube_api_key")
    return build("youtube", "v3", developerKey=API_KEY)


def fetch_video_ids(youtube, team_name):
    published_after = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
    search_response = (
        youtube.search()
        .list(
            q=f"{team_name} FULL GAME HIGHLIGHTS highlights full game",
            part="id,snippet",
            type="video",
            maxResults=3,  # Adjusts the number of videos
            channelId="UCWJ2lWNubArHWmf3FIHbfcQ",  # NBA Official Youtube Channel ID
            publishedAfter=published_after,
        )
        .execute()
    )
    videos = search_response.get("items", [])
    return [video["id"]["videoId"] for video in videos]


def fetch_comments(youtube, video_id, nlp, team_name, total_max_results):
    comments = []
    current_results = 0
    max_results_per_page = 100
    next_page_token = None

    while current_results < total_max_results:
        results_to_retrieve = min(
            total_max_results - current_results, max_results_per_page
        )

        comments_response = (
            youtube.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=results_to_retrieve,
                pageToken=next_page_token,
            )
            .execute()
        )

        for comment in comments_response.get("items", []):
            comment_text = comment["snippet"]["topLevelComment"]["snippet"][
                "textDisplay"
            ]
            doc = nlp(comment_text)

            if any(entity.text.lower() in team_name.lower() for entity in doc.ents):
                comments.append(comment_text)
                current_results += 1

        next_page_token = comments_response.get("nextPageToken")
        if not next_page_token or current_results >= total_max_results:
            break

    return comments


def analyze_sentiment(request):
    if request.method == "POST":
        selected_team = request.POST.get("selected_team", "")

        # Get team data from Database
        existing_team_sentiment = TeamSentiment.objects.filter(
            team_name=selected_team
        ).first()

        # Get the compound score
        avg_compound_score = existing_team_sentiment.avg_compound_score

        return render(
            request,
            "sentiment/team_detail.html",
            {"team": selected_team, "score": avg_compound_score},
        )

    return render(request, "sentiment/team_detail.html")


def home(request):
    text = request.POST.get("teams_name", "")
    teams_results = []

    if request.method == "POST" and text:
        teams_results = teams.find_teams_by_full_name(text)

    return render(
        request, "sentiment/home.html", {"text": text, "teams_results": teams_results}
    )


def run_sentiment_analysis_for_all_teams():
    # Get all NBA teams
    nba_teams = teams.get_teams()

    # Initialize YouTube API
    youtube = initialize_youtube_api()

    # Initialize spaCy
    nlp = spacy.load("en_core_web_sm")

    for team in nba_teams:
        team_name = team["full_name"]

        # Fetch video ids for the current team
        video_ids = fetch_video_ids(youtube, team_name)

        # Fetch comments and perform sentiment analysis
        comments = []
        for video_id in video_ids:
            comments += fetch_comments(
                youtube, video_id, nlp, team_name, total_max_results=250
            )

        comments_text = "\n".join(comments)

        sia = SentimentIntensityAnalyzer()

        polarity = np.array(
            [sia.polarity_scores(comment)["compound"] for comment in comments]
        )

        avg_compound_score = np.mean(polarity)

        # Normalize to a percentage and round
        avg_compound_score = ((avg_compound_score - -0.1) / (0.6 - -0.1)) * (100)
        avg_compound_score = round(avg_compound_score, 1)

        if avg_compound_score < 0:
            avg_compound_score = 0

        # Check for duplicate team name
        existing_team_sentiment = TeamSentiment.objects.filter(
            team_name=team_name
        ).first()

        if existing_team_sentiment:
            # Update the existing record if necessary
            existing_team_sentiment.avg_compound_score = avg_compound_score
            existing_team_sentiment.save()
        else:
            # Create a new record if no duplicate is found
            team_sentiment = TeamSentiment(
                team_name=team_name, avg_compound_score=avg_compound_score
            )
            try:
                team_sentiment.save()
            except IntegrityError:
                # Handle the case where another thread or process created the same record concurrently
                pass
    last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Uncomment the line below to run sentiment analysis for all NBA teams (UPDATE DATABASE)
# run_sentiment_analysis_for_all_teams()


def rankings(request):
    # Fetch all team sentiment data, ordered by average compound score
    team_sentiments = TeamSentiment.objects.all().order_by("-avg_compound_score")

    return render(
        request,
        "sentiment/rankings.html",
        {"team_sentiments": team_sentiments, "last_update_time": last_update_time},
    )


def about(request):
    return render(request, "sentiment/about.html")


def team_detail(request, team_name):
    team = get_object_or_404(TeamSentiment, team_name=team_name)
    return render(
        request,
        "sentiment/team_detail.html",
        {"team": team, "score": team.avg_compound_score},
    )


def analysis(request):
    return render(request, "sentiment/analysis.html")


def get_team_data(request):
    team = NBATeam.objects.get(team_name=request.GET.get("team_name"))
    context = {"team": team}
    html = render(request, "sentiment/team_data.html", context)
    return HttpResponse(html)
