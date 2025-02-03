import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}
    
    def fetch_stock_data(self, symbol, period='1mo'):
        """Fetch stock data from Yahoo Finance"""
        # Convert Saudi stock symbol to Yahoo Finance format
        yahoo_symbol = f"{symbol}.SR"
        stock = yf.Ticker(yahoo_symbol)
        df = stock.history(period=period)
        return df
    
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Calculate moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Volume analysis
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        return df
    
    def get_trading_signals(self, df):
        """Generate trading signals based on technical analysis"""
        latest = df.iloc[-1]
        signals = []
        
        # Moving Average signals
        if latest['Close'] > latest['SMA_20'] and latest['SMA_20'] > latest['SMA_50']:
            signals.append(("MA Trend", "Bullish", "🟢"))
        elif latest['Close'] < latest['SMA_20'] and latest['SMA_20'] < latest['SMA_50']:
            signals.append(("MA Trend", "Bearish", "🔴"))
        else:
            signals.append(("MA Trend", "Neutral", "🟡"))
        
        # RSI signals
        if latest['RSI'] > 70:
            signals.append(("RSI", "Overbought", "🔴"))
        elif latest['RSI'] < 30:
            signals.append(("RSI", "Oversold", "🟢"))
        else:
            signals.append(("RSI", "Neutral", "🟡"))
        
        # MACD signals
        if latest['MACD'] > latest['Signal_Line']:
            signals.append(("MACD", "Bullish", "🟢"))
        else:
            signals.append(("MACD", "Bearish", "🔴"))
        
        # Volume analysis
        if latest['Volume_Ratio'] > 1.5:
            signals.append(("Volume", "High", "🟢"))
        elif latest['Volume_Ratio'] < 0.5:
            signals.append(("Volume", "Low", "🔴"))
        else:
            signals.append(("Volume", "Average", "🟡"))
        
        return signals
    
    def get_recommendation(self, signals, sentiment_score):
        """Generate trading recommendation based on technical and sentiment analysis"""
        bullish_signals = sum(1 for _, signal, _ in signals if signal in ["Bullish", "Oversold", "High"])
        bearish_signals = sum(1 for _, signal, _ in signals if signal in ["Bearish", "Overbought", "Low"])
        
        # Combine technical signals with sentiment
        if sentiment_score > 0.6:
            bullish_signals += 1
        elif sentiment_score < 0.4:
            bearish_signals += 1
        
        # Generate recommendation
        if bullish_signals > bearish_signals + 1:
            return {
                "action": "Strong Buy",
                "confidence": "High",
                "emoji": "🟢",
                "risk_level": "Medium"
            }
        elif bullish_signals > bearish_signals:
            return {
                "action": "Buy",
                "confidence": "Medium",
                "emoji": "🟢",
                "risk_level": "Medium-High"
            }
        elif bearish_signals > bullish_signals + 1:
            return {
                "action": "Strong Sell",
                "confidence": "High",
                "emoji": "🔴",
                "risk_level": "High"
            }
        elif bearish_signals > bullish_signals:
            return {
                "action": "Sell",
                "confidence": "Medium",
                "emoji": "🔴",
                "risk_level": "Medium-High"
            }
        else:
            return {
                "action": "Hold",
                "confidence": "Low",
                "emoji": "🟡",
                "risk_level": "Low"
            } 
