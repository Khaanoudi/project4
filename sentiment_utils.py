def get_sentiment_category(score):
    """Determine sentiment category based on score"""
    if score > 0.6:
        return "Positive"
    elif score < 0.4:
        return "Negative"
    return "Neutral"

def get_sentiment_style(score):
    """Get styling elements for a sentiment score"""
    if score > 0.6:
        return {
            "color": "#28a745",  # Green
            "emoji": "🟢",
            "category": "Positive"
        }
    elif score < 0.4:
        return {
            "color": "#dc3545",  # Red
            "emoji": "🔴",
            "category": "Negative"
        }
    return {
        "color": "#ffc107",  # Yellow
        "emoji": "🟡",
        "category": "Neutral"
    }

def create_sentiment_card_html(entity, score):
    """Generate HTML for a sentiment card"""
    style = get_sentiment_style(score)
    
    return f"""
    <div style='padding: 15px; border-radius: 10px; background-color: rgba(0,0,0,0.05); margin-bottom: 10px;'>
        <h4 style='margin: 0; color: {style["color"]};'>{style["emoji"]} {entity['name']}</h4>
        <p style='color: gray; font-size: 0.8em; margin: 5px 0;'>{entity['symbol']}</p>
        <div style='margin: 10px 0;'>
            <div style='
                width: {score * 100}%;
                height: 8px;
                background-color: {style["color"]};
                border-radius: 4px;
            '></div>
        </div>
        <p style='text-align: right; color: {style["color"]}; font-weight: bold; margin: 0;'>
            {score:.2f} | {style["category"]}
        </p>
    </div>
    """

def filter_articles_by_sentiment(articles, sentiment_filter):
    """Filter articles based on sentiment categories"""
    filtered_articles = []
    for article in articles:
        if article.get("entities"):
            article_sentiments = [
                get_sentiment_category(entity["sentiment_score"]) 
                for entity in article["entities"] 
                if "sentiment_score" in entity
            ]
            if any(sentiment in sentiment_filter for sentiment in article_sentiments):
                filtered_articles.append(article)
    return filtered_articles 
