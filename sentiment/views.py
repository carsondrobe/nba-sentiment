from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import teams
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from statistics import mean
import spacy
import numpy as np


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
        youtube = initialize_youtube_api()
        video_ids = fetch_video_ids(youtube, selected_team)
        nlp = spacy.load("en_core_web_sm")

        comments = []
        for video_id in video_ids:
            comments += fetch_comments(
                youtube, video_id, nlp, selected_team, total_max_results=250
            )

        comments_text = "\n".join(comments)

        sia = SentimentIntensityAnalyzer()

        polarity = np.array(
            [sia.polarity_scores(comment)["compound"] for comment in comments]
        )

        positive_comments = np.array(comments)[polarity > 0.05].tolist()
        negative_comments = np.array(comments)[polarity < -0.05].tolist()
        neutral_comments = np.array(comments)[
            (polarity >= -0.05) & (polarity <= 0.05)
        ].tolist()

        avg_compound_score = np.mean(polarity)

        # Normalize to a percentage and round
        avg_compound_score = ((avg_compound_score - -0.1) / (0.6 - -0.1)) * (100)
        avg_compound_score = round(avg_compound_score, 1)

        return render(
            request,
            "sentiment/sentiment_analysis.html",
            {
                "selected_team": selected_team,
                "avg_compound_score": avg_compound_score,
                "positive_comments": positive_comments,
                "negative_comments": negative_comments,
                "neutral_comments": neutral_comments,
            },
        )

    return render(request, "sentiment/sentiment_analysis.html")


def home(request):
    text = request.POST.get("teams_name", "")
    teams_results = []

    if request.method == "POST" and text:
        teams_results = teams.find_teams_by_full_name(text)

    return render(
        request, "sentiment/home.html", {"text": text, "teams_results": teams_results}
    )
