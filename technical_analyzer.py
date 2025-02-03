import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}
    
    def fetch_stock_data(self, symbol, period='1mo'):
        """Fetch stock data from Yahoo Finance"""
        try:
            # Convert Saudi stock symbol to Yahoo Finance format
            yahoo_symbol = f"{symbol}.SR"
            stock = yf.Ticker(yahoo_symbol)
            df = stock.history(period=period)
            
            # Check if we have enough data
            if len(df) < 2:
                raise ValueError(f"Insufficient data for {symbol}")
                
            return df
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {str(e)}")
    
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        try:
            if len(df) < 50:  # Need at least 50 data points for all indicators
                # Use smaller windows for limited data
                sma_fast = min(10, len(df) - 1)
                sma_slow = min(20, len(df) - 1)
                rsi_period = min(7, len(df) - 1)
            else:
                sma_fast = 20
                sma_slow = 50
                rsi_period = 14
            
            # Calculate moving averages
            df['SMA_20'] = df['Close'].rolling(window=sma_fast).mean()
            df['SMA_50'] = df['Close'].rolling(window=sma_slow).mean()
            
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD with adjusted periods for limited data
            macd_fast = min(12, len(df) - 1)
            macd_slow = min(26, len(df) - 1)
            macd_signal = min(9, len(df) - 1)
            
            exp1 = df['Close'].ewm(span=macd_fast, adjust=False).mean()
            exp2 = df['Close'].ewm(span=macd_slow, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()
            
            # Volume analysis
            df['Volume_MA'] = df['Volume'].rolling(window=min(20, len(df) - 1)).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
            
            # Fill NaN values with reasonable defaults
            df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
            
            return df
        except Exception as e:
            raise ValueError(f"Error calculating indicators: {str(e)}")
    
    def get_trading_signals(self, df):
        """Generate trading signals based on technical analysis"""
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            signals = []
            
            # Trend signals based on recent price action
            price_change = (latest['Close'] - prev['Close']) / prev['Close']
            
            # Moving Average signals
            if latest['Close'] > latest['SMA_20'] and latest['SMA_20'] > latest['SMA_50']:
                signals.append(("Trend", "Bullish", "🟢"))
            elif latest['Close'] < latest['SMA_20'] and latest['SMA_20'] < latest['SMA_50']:
                signals.append(("Trend", "Bearish", "🔴"))
            else:
                signals.append(("Trend", "Neutral", "🟡"))
            
            # Momentum signals
            if latest['RSI'] > 70:
                signals.append(("Momentum", "Overbought", "🔴"))
            elif latest['RSI'] < 30:
                signals.append(("Momentum", "Oversold", "🟢"))
            else:
                signals.append(("Momentum", "Neutral", "🟡"))
            
            # Volume signals
            if latest['Volume_Ratio'] > 1.5:
                signals.append(("Volume", "High Activity", "🟢"))
            elif latest['Volume_Ratio'] < 0.5:
                signals.append(("Volume", "Low Activity", "🔴"))
            else:
                signals.append(("Volume", "Normal", "🟡"))
            
            # Price Action
            if price_change > 0.02:  # 2% up
                signals.append(("Price", "Strong Up", "🟢"))
            elif price_change < -0.02:  # 2% down
                signals.append(("Price", "Strong Down", "🔴"))
            else:
                signals.append(("Price", "Stable", "🟡"))
            
            return signals
        except Exception as e:
            raise ValueError(f"Error generating signals: {str(e)}")
    
    def get_recommendation(self, signals, sentiment_score):
        """Generate trading recommendation based on technical and sentiment analysis"""
        try:
            bullish_signals = sum(1 for _, signal, _ in signals if "Bullish" in signal or "Up" in signal or "High" in signal)
            bearish_signals = sum(1 for _, signal, _ in signals if "Bearish" in signal or "Down" in signal or "Low" in signal)
            
            # Add sentiment weight
            if sentiment_score > 0.6:
                bullish_signals += 1
            elif sentiment_score < 0.4:
                bearish_signals += 1
            
            # Calculate confidence based on signal strength
            total_signals = len(signals) + 1  # +1 for sentiment
            confidence = max(bullish_signals, bearish_signals) / total_signals
            
            if confidence > 0.7:
                confidence_level = "High"
            elif confidence > 0.5:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"
            
            # Generate recommendation
            if bullish_signals > bearish_signals + 1:
                return {
                    "action": "Strong Buy",
                    "confidence": confidence_level,
                    "emoji": "🟢",
                    "risk_level": "Medium"
                }
            elif bullish_signals > bearish_signals:
                return {
                    "action": "Buy",
                    "confidence": confidence_level,
                    "emoji": "🟢",
                    "risk_level": "Medium-High"
                }
            elif bearish_signals > bullish_signals + 1:
                return {
                    "action": "Strong Sell",
                    "confidence": confidence_level,
                    "emoji": "🔴",
                    "risk_level": "High"
                }
            elif bearish_signals > bullish_signals:
                return {
                    "action": "Sell",
                    "confidence": confidence_level,
                    "emoji": "🔴",
                    "risk_level": "Medium-High"
                }
            else:
                return {
                    "action": "Hold",
                    "confidence": confidence_level,
                    "emoji": "🟡",
                    "risk_level": "Low"
                }
        except Exception as e:
            raise ValueError(f"Error generating recommendation: {str(e)}") 
