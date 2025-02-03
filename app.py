import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from sentiment_analyzer import SentimentAnalyzer
from technical_analyzer import TechnicalAnalyzer
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Initialize technical analyzer
@st.cache_resource
def get_technical_analyzer():
    return TechnicalAnalyzer()

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

def plot_technical_chart(df, symbol):
    """Create an interactive technical analysis chart"""
    fig = make_subplots(rows=3, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.03,
                       row_heights=[0.6, 0.2, 0.2])
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ), row=1, col=1)
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_20'],
        name='SMA 20',
        line=dict(color='orange')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_50'],
        name='SMA 50',
        line=dict(color='blue')
    ), row=1, col=1)
    
    # Volume chart
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        name='Volume',
        marker_color='rgba(0,0,255,0.3)'
    ), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'],
        name='RSI',
        line=dict(color='purple')
    ), row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        yaxis_title='Price',
        yaxis2_title='Volume',
        yaxis3_title='RSI',
        xaxis_rangeslider_visible=False,
        height=800
    )
    
    return fig

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

    # Add technical analysis after sentiment
    if article.get("entities"):
        for entity in article["entities"]:
            if "sentiment_score" in entity:
                display_company_analysis(entity)

def display_company_analysis(entity):
    """Display technical analysis for a single company"""
    try:
        analyzer = get_technical_analyzer()
        
        # Fetch and analyze stock data
        df = analyzer.fetch_stock_data(entity['symbol'])
        df = analyzer.calculate_indicators(df)
        signals = analyzer.get_trading_signals(df)
        recommendation = analyzer.get_recommendation(
            signals, 
            entity.get("sentiment_score", 0.5)
        )
        
        # Create expandable section for technical analysis
        with st.expander(f"📊 Technical Analysis for {entity['name']}", expanded=True):
            # Price and Volume metrics
            col1, col2, col3 = st.columns(3)
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            with col1:
                price_change = ((latest['Close']/prev['Close'])-1)*100
                st.metric(
                    "Current Price",
                    f"SAR {latest['Close']:.2f}",
                    f"{price_change:+.2f}%"
                )
            
            with col2:
                volume_change = ((latest['Volume']/prev['Volume'])-1)*100
                st.metric(
                    "Volume",
                    f"{int(latest['Volume']:,)}",
                    f"{volume_change:+.2f}%"
                )
            
            with col3:
                st.metric("RSI", f"{latest['RSI']:.2f}")
            
            # Trading signals in a compact format
            st.markdown("##### Trading Signals:")
            signal_cols = st.columns(len(signals))
            for col, (indicator, signal, emoji) in zip(signal_cols, signals):
                with col:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 8px; background-color: #f8f9fa; 
                         border-radius: 5px; margin: 2px;'>
                        <p style='margin: 0; font-weight: bold;'>{emoji} {indicator}</p>
                        <p style='margin: 0; font-size: 0.9em;'>{signal}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recommendation
            st.markdown("##### Recommendation:")
            st.markdown(f"""
            <div style='padding: 10px; background-color: {
                "#d4edda" if recommendation["action"].startswith("Buy")
                else "#f8d7da" if recommendation["action"].startswith("Sell")
                else "#fff3cd"
            }; border-radius: 5px; margin: 5px 0;'>
                <h4 style='margin: 0; text-align: center;'>
                    {recommendation["emoji"]} {recommendation["action"]}
                </h4>
                <p style='margin: 5px 0; text-align: center; font-size: 0.9em;'>
                    Confidence: {recommendation["confidence"]} | Risk: {recommendation["risk_level"]}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Technical chart
            fig = plot_technical_chart(df, entity['symbol'])
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Unable to analyze {entity['symbol']}: {str(e)}")

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
        filtered_articles = filter_articles_by_sentiment(
            news_data["data"], 
            sentiment_filter
        )
        
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
                        st.markdown("### Related Companies Analysis")
                        for entity in article["entities"]:
                            st.markdown(f"#### {entity['name']} ({entity['symbol']})")
                            display_company_analysis(entity)
                    
                    st.markdown(f"[Read full article]({article['url']})")
                
                st.markdown("---")
    else:
        st.warning("No news data available at the moment.")

if __name__ == "__main__":
    main() 
