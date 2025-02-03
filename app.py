import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from sentiment_analyzer import SentimentAnalyzer

# Configure the page
st.set_page_config(
    page_title="Saudi Stock Market News",
    page_icon="📈",
    layout="wide"
)

# API configuration
API_KEY = "bS2jganHVlFYtAly7ttdHYLrTB0s6BmONWmFEApD"
BASE_URL = "https://api.stockdata.org/v1/news/all"

# Initialize sentiment analyzer
@st.cache_resource
def get_sentiment_analyzer():
    return SentimentAnalyzer()

def fetch_news(days_ago=7):
    # Calculate date N days ago
    published_after = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M")
    
    params = {
        "countries": "sa",
        "filter_entities": "true",
        "limit": 2,  # Reduced to match API limit
        "published_after": published_after,
        "api_token": API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_sentiment_category(score):
    if score > 0.6:
        return "Positive"
    elif score < 0.4:
        return "Negative"
    return "Neutral"

def display_sentiment_comparison(entity, text, parent_container):
    """Display comparison between API and calculated sentiment"""
    analyzer = get_sentiment_analyzer()
    
    if "sentiment_score" in entity:
        comparison = analyzer.get_sentiment_comparison(
            entity["sentiment_score"],
            text
        )
        
        # Create a card-like container for comparison
        parent_container.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h4 style='color: #495057; margin-bottom: 15px;'>📊 Sentiment Analysis Comparison</h4>
            <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                <div>
                    <p style='color: #6c757d; font-size: 0.9em; margin: 0;'>API Score</p>
                    <p style='font-size: 1.2em; font-weight: bold; margin: 0;'>{comparison['api_score']:.2f}</p>
                </div>
                <div>
                    <p style='color: #6c757d; font-size: 0.9em; margin: 0;'>Calculated Score</p>
                    <p style='font-size: 1.2em; font-weight: bold; margin: 0;'>{comparison['calculated_score']:.2f}</p>
                </div>
            </div>
            <div style='background-color: white; padding: 10px; border-radius: 5px; text-align: center;'>
                <p style='margin: 0; font-weight: bold;'>Agreement Level: {
                    "🟢 High" if comparison['agreement'] == 'High'
                    else "🟡 Medium" if comparison['agreement'] == 'Medium'
                    else "🔴 Low"
                }</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_sentiment(article):
    """Helper function to display sentiment information"""
    if article.get("entities"):
        # Create a container for each article's sentiment analysis
        with st.container():
            st.markdown("""
            <div style='border-left: 4px solid #007bff; padding-left: 15px; margin: 20px 0;'>
                <h3 style='color: #007bff;'>📊 Market Sentiment Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create columns for multiple entities
            num_entities = len(article["entities"])
            if num_entities > 0:
                cols = st.columns(min(num_entities, 2))
                
                for idx, entity in enumerate(article["entities"]):
                    if "sentiment_score" in entity:
                        col_idx = idx % 2
                        with cols[col_idx]:
                            score = entity["sentiment_score"]
                            
                            # Determine sentiment category and color
                            if score > 0.6:
                                color = "#28a745"
                                emoji = "🟢"
                                category = "Positive"
                            elif score < 0.4:
                                color = "#dc3545"
                                emoji = "🔴"
                                category = "Negative"
                            else:
                                color = "#ffc107"
                                emoji = "🟡"
                                category = "Neutral"
                            
                            # Enhanced company card
                            st.markdown(f"""
                            <div style='
                                background-color: white;
                                border: 1px solid {color}33;
                                border-radius: 10px;
                                padding: 15px;
                                margin-bottom: 15px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                            '>
                                <div style='
                                    background-color: {color}11;
                                    padding: 10px;
                                    border-radius: 8px;
                                    margin-bottom: 10px;
                                '>
                                    <h4 style='margin: 0; color: {color};'>{emoji} {entity['name']}</h4>
                                    <p style='color: #6c757d; font-size: 0.8em; margin: 5px 0;'>{entity['symbol']}</p>
                                </div>
                                <div style='margin: 15px 0;'>
                                    <div style='
                                        width: {score * 100}%;
                                        height: 8px;
                                        background-color: {color};
                                        border-radius: 4px;
                                        transition: width 0.3s ease;
                                    '></div>
                                </div>
                                <p style='
                                    text-align: right;
                                    color: {color};
                                    font-weight: bold;
                                    margin: 0;
                                    font-size: 1.1em;
                                '>
                                    {score:.2f} | {category}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add sentiment comparison within the same column
                            display_sentiment_comparison(
                                entity,
                                f"{article['title']} {article['description']}",
                                st
                            )

def main():
    st.title("🇸🇦 Saudi Stock Market News")
    
    # Add filters in sidebar
    st.sidebar.title("Filters")
    
    # Date range filter
    days_ago = st.sidebar.slider("News from last N days", 1, 30, 7)
    
    # Sentiment filter
    sentiment_filter = st.sidebar.multiselect(
        "Filter by Sentiment",
        ["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"]
    )
    
    # Add refresh button with loading state
    if st.button("🔄 Refresh News"):
        with st.spinner("Fetching latest news..."):
            st.experimental_rerun()
    
    # Fetch and display news
    news_data = fetch_news(days_ago)
    
    if news_data and "data" in news_data:
        # Filter articles based on sentiment
        filtered_articles = []
        for article in news_data["data"]:
            if article.get("entities"):
                article_sentiments = [get_sentiment_category(entity["sentiment_score"]) 
                                   for entity in article["entities"] 
                                   if "sentiment_score" in entity]
                if any(sentiment in sentiment_filter for sentiment in article_sentiments):
                    filtered_articles.append(article)
        
        # Display total articles found
        st.caption(f"Found {len(filtered_articles)} articles matching your filters")
        
        for article in filtered_articles:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if article.get("image_url"):
                        st.image(article["image_url"], use_container_width=True)
                    display_sentiment(article)
                
                with col2:
                    st.markdown(f"### {article['title']}")
                    st.markdown(f"📅 *{article['published_at'][:10]}*")
                    st.write(article["description"])
                    
                    if article.get("entities"):
                        st.markdown("**Related Companies:**")
                        for entity in article["entities"]:
                            st.markdown(f"- {entity['name']} ({entity['symbol']})")
                    
                    st.markdown(f"[Read full article]({article['url']})")
                
                st.markdown("---")
    else:
        st.warning("No news data available at the moment.")

if __name__ == "__main__":
    main() 
