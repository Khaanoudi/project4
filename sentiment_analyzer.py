from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text):
        """Analyze text using multiple methods and return combined sentiment"""
        if not text:
            return 0.5  # Neutral score for empty text
        
        # VADER sentiment analysis
        vader_scores = self.sia.polarity_scores(text)
        vader_compound = (vader_scores['compound'] + 1) / 2  # Normalize to 0-1
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_score = (blob.sentiment.polarity + 1) / 2  # Normalize to 0-1
        
        # Combine scores (simple average)
        combined_score = np.mean([vader_compound, textblob_score])
        
        return combined_score
    
    def get_sentiment_comparison(self, api_score, text):
        """Compare API sentiment with calculated sentiment"""
        calculated_score = self.analyze_text(text)
        
        return {
            'api_score': api_score,
            'calculated_score': calculated_score,
            'difference': abs(api_score - calculated_score),
            'agreement': 'High' if abs(api_score - calculated_score) < 0.2 else 
                        'Medium' if abs(api_score - calculated_score) < 0.4 else 
                        'Low'
        } 
