# NBA Sentiment Analysis

An application to analyze NBA team fan sentiment on YouTube through Django, NLTK, spaCy, and YouTube Data API.

## Overview

NBA Sentiment Analysis is a Django web application designed to provide insights into the sentiment of YouTube comments related to NBA teams' full game highlights. Leveraging natural language processing (NLP) libraries such as NLTK and spaCy, the application categorizes comments as positive, negative, or neutral, contributing to an overall sentiment score.

## Features

- **YouTube Data API Integration:**
  - Fetches video comments from the NBA's official YouTube channel using YouTube Data API v3.

- **Sentiment Analysis:**
  - Utilizes NLTK's SentimentIntensityAnalyzer to perform sentiment analysis on gathered comments.

- **Named Entity Recognition (spaCy):**
  - Filters relevant comments using spaCy's named entity recognition to ensure the analysis focuses on the specific NBA team.

- **Dynamic Thresholds:**
  - Fine-tuned polarity score thresholds for accurate categorization of sentiment related to an NBA team.

## How to Use

1. Clone the repository to your local machine.
2. Set up a virtual environment and install dependencies.
3. Obtain a YouTube API key and set it in the environment variables (dotenv).
4. Run the Django development server.
5. Access the application in your web browser.

## Requirements

- Django
- NLTK
- spaCy
- NumPy
- Google API Client

## Getting Started

To get started with NBA Sentiment Analysis, follow these steps:

```bash
# Clone the repository
git clone https://github.com/your_username/NBA-Sentiment-Analysis.git

# Navigate to the project directory
cd NBA-Sentiment-Analysis

# Set up virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
