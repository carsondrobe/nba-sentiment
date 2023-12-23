from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from nba_api.stats.static import teams
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from statistics import mean


def analyze_sentiment(request):
    if request.method == "POST":
        selected_team = request.POST.get("selected_team", "")
        comments = youtube_analysis(selected_team)

        # Join comments into a single string
        comments_text = "\n".join(comments)
        print(comments_text)

        sia = SentimentIntensityAnalyzer()

        # Calculate sentiment scores for each comment
        comment_sentiments = [sia.polarity_scores(comment) for comment in comments]

        # Calculate average sentiment scores
        avg_sentiment_scores = {
            "pos": mean(comment["pos"] for comment in comment_sentiments),
            "neu": mean(comment["neu"] for comment in comment_sentiments),
            "neg": mean(comment["neg"] for comment in comment_sentiments),
            "compound": mean(comment["compound"] for comment in comment_sentiments),
        }
        print(avg_sentiment_scores)

        return render(
            request,
            "sentiment/sentiment_analysis.html",  # Adjust the path based on your template structure
            {
                "selected_team": selected_team,
                "sentiment_scores": avg_sentiment_scores,
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
            maxResults=1,  # Adjust the number of results as needed
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

    # TODO: Get Comments from the video IDs
    query = team_name
    query_list = query.split()
    filtered_comments = []
    for video_id in video_id_list:
        # Set initial values
        max_results_per_page = 100
        total_max_results = 100
        current_results = 0
        next_page_token = None

        # Collect comments from multiple pages
        while current_results < total_max_results:
            # Calculate the number of results to retrieve on this page
            remaining_results = total_max_results - current_results
            results_to_retrieve = min(remaining_results, max_results_per_page)

            # Get comments for the current page
            comments_response = (
                youtube.commentThreads()
                .list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=results_to_retrieve,
                    pageToken=next_page_token,  # Include the nextPageToken in the request
                )
                .execute()
            )

            # Extract comments from the current page
            for comment in comments_response.get("items", []):
                comment_text = comment["snippet"]["topLevelComment"]["snippet"][
                    "textDisplay"
                ]
                if any(word.lower() in comment_text.lower() for word in query_list):
                    filtered_comments.append(comment_text)
                    current_results += 1

            # Check if there are more pages
            next_page_token = comments_response.get("nextPageToken")
            if not next_page_token:
                break
    return filtered_comments
